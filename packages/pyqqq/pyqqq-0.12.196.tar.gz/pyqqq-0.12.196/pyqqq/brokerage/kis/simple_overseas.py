from dataclasses import asdict
from decimal import Decimal
from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.brokerage.kis.overseas_stock import KISOverseasStock
from pyqqq.data.overseas import get_ticker_info
from pyqqq.datatypes import *
from pyqqq.utils.limiter import CallLimiter
from pyqqq.utils.local_cache import ttl_cache
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo
import datetime as dtm
import pandas as pd


class KISSimpleOverseasStock:
    """
    한국투자증권 해외 주식 API 사용하여 주식 거래를 하기 위한 클래스 입니다.

    기존 KISOverseasStock 클래쓰를 감싸고, 간편한 주문/조회 기능을 제공합니다.
    아래와 같은 제약 사항이 있습니다.

    - 미국 주식만 지원 (NYSE, NASDAQ, AMEX)
    - 정규장 거래만 지원 (시간외 거래 미지원)
    - 외화 거래만 지원 (통합증거금 불가)

    Attributes:
        auth (KISAuth): 한국투자증권 API 인증 정보.
        account_no (str): 계좌 번호.
        account_product_code (str): 계좌 상품 코드.
        hts_id (Optional[str]): HTS ID (해외주식 계좌 식별자).
    """

    nyt = ZoneInfo("America/New_York")
    kst = ZoneInfo("Asia/Seoul")

    def __init__(
        self,
        auth: KISAuth,
        account_no: str,
        account_product_code: str,
        hts_id: Optional[str] = None,
    ):
        self.auth = auth
        self.account_no = account_no
        self.account_product_code = account_product_code
        self.currency_code = "USD"
        self.hts_id = hts_id

        self.stock_api = KISOverseasStock(auth)

    def get_supported_exchange_codes(self) -> List[str]:
        return ["NYSE", "NASD", "AMEX"]

    def get_account(self) -> Dict:
        """
        계좌 요약 정보를 조회하여 총 잔고, 투자 가능 현금, 매입 금액 및 손익 정보를 반환합니다.

        이 메서드는 계좌의 현재 보유 포지션, 대기 중인 주문, 외화 증거금 정보를 수집하여
        총 잔고, 투자 가능 현금, 매입 금액, 평가 금액, 손익(PnL) 및 손익률을 계산합니다.

        Returns:
            dict: 계좌 요약 정보를 포함하는 딕셔너리로 반환합니다.
                - total_balance (float): 평가 자산 및 대기 주문을 포함한 총 잔고.
                - investable_cash (float): 신규 주문에 사용 가능한 현금.
                - purchase_amount (float): 현재 보유한 포지션의 총 매입 금액.
                - evaluated_amount (float): 현재 보유한 포지션의 평가 금액.
                - pnl_amount (float): 평가 금액과 매입 금액을 바탕으로 계산한 손익.
                - pnl_rate (float): 손익률 (손익 / 매입 금액 * 100).
        """
        foreign_margin = self._get_foreign_margin_usd()

        positions = self._get_positions()

        purchase_amount = sum([p["purchase_value"] for p in positions])
        evaluated_amount = sum([p["current_value"] for p in positions])
        pnl_amount = evaluated_amount - purchase_amount
        pnl_rate = 0 if purchase_amount == 0 else pnl_amount / purchase_amount * 100

        holding_balance = 0
        for p in self.get_pending_orders():
            if p.side == OrderSide.BUY:
                holding_balance += p.price * p.quantity

        order_possible_amount = foreign_margin["order_possible_amount"]
        total_balance = order_possible_amount + evaluated_amount + holding_balance

        result = {
            "total_balance": total_balance,
            "investable_cash": order_possible_amount,
            "purchase_amount": purchase_amount,
            "evaluated_amount": evaluated_amount,
            "pnl_amount": pnl_amount,
            "pnl_rate": pnl_rate,
        }

        return result

    def _get_foreign_margin_usd(self):
        r = self.stock_api.get_foreign_margin(self.account_no, self.account_product_code)
        usd = None
        for data in r["output"]:
            if data["crcy_cd"] == "USD":
                usd = data
                break

        # 외화 예수 금액
        deposit_amount = Decimal(usd["frcr_dncl_amt1"])
        # 외화 일반 주문 가능 금액
        order_possible_amount = Decimal(usd["frcr_gnrl_ord_psbl_amt"])
        # 미결제 매수 금액
        unsettled_buy_amount = Decimal(usd["ustl_buy_amt"])
        # 미결제 매도 금액
        unsettled_sell_amount = Decimal(usd["ustl_sll_amt"])

        return {
            "deposit_amount": deposit_amount,
            "order_possible_amount": order_possible_amount,
            "unsettled_buy_amount": unsettled_buy_amount,
            "unsettled_sell_amount": unsettled_sell_amount,
        }

    def _get_positions(self):
        # 거래소 코드를 NASD로 조회하면 미국전체에 대한 포지션을 조회할 수 있음 (KIS developer)
        r = self.stock_api.inquire_balance(
            self.account_no,
            self.account_product_code,
            "NASD",
            self.currency_code,
        )

        positions = []

        for data in r["output1"]:
            positions.append(
                {
                    "ticker": data["ovrs_pdno"],
                    "name": data["ovrs_item_name"],
                    "pnl": data["frcr_evlu_pfls_amt"],
                    "pnl_rate": data["evlu_pfls_rt"],
                    "qty": data["ovrs_cblc_qty"],
                    "sell_possible_qty": data["ord_psbl_qty"],
                    "purchase_value": data["frcr_pchs_amt1"],
                    "current_value": data["ovrs_stck_evlu_amt"],
                    "current_price": data["now_pric2"],
                    "average_purchase_price": data["pchs_avg_pric"],
                    "exchange": data["ovrs_excg_cd"],
                    "currency": data["tr_crcy_cd"],
                }
            )

        return positions

    def get_possible_quantity(
        self,
        ticker: str,
        price: Optional[Decimal] = None,
    ) -> Dict:
        """
        특정 티커에 대해 지정된 가격으로 주문 가능한 최대 수량과 금액을 조회합니다.

        Args:
            ticker (str): 조회할 자산의 티커(symbol).
            price (Optional[Decimal], optional): 조회할 가격. 지정하지 않으면 현재 가격을 사용. 기본값은 None.

        Returns:
            dict: 주문 가능한 수량 및 금액 정보.
                - currency (str): 거래 통화 코드.
                - possible_amount (Decimal): 주문 가능한 금액.
                - quantity (int): 주문 가능한 최대 수량.
                - price (Decimal): 조회된 가격.

        Raises:
            ValueError: 유효하지 않은 티커나 지원되지 않는 거래소인 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Unknown ticker {ticker}")

        exchange = ticker_info["exchange"].loc[ticker]
        if exchange not in self.get_supported_exchange_codes():
            raise ValueError(f"Unsupported exchange code {exchange}")

        if price is None:
            price = self._get_cached_price(ticker)

        r = self.stock_api.inquire_psamount(
            self.account_no,
            self.account_product_code,
            exchange,
            price,
            ticker,
        )

        output = r["output"]

        result = {
            "currency": output["tr_crcy_cd"],
            "possible_amount": output["ovrs_ord_psbl_amt"],
            "quantity": output["max_ord_psbl_qty"],
            "price": price,
        }

        return result

    def get_positions(self, to_frame: bool = False) -> List[StockPosition] | pd.DataFrame:
        """
        보유 포지션 정보를 조회하여 리스트 또는 데이터프레임 형식으로 반환합니다.

        Args:
            to_frame (bool, optional): True일 경우 Pandas DataFrame으로 반환, False일 경우 리스트 형식의 StockPosition 객체들로 반환. 기본값은 False.

        Returns:
            List[StockPosition] | pd.DataFrame: 보유 포지션 정보를 포함한 리스트 또는 DataFrame.
                - 리스트 형식 (StockPosition 객체들):
                    - asset_code (str): 자산 티커 코드.
                    - asset_name (str): 자산 이름.
                    - quantity (float): 보유 수량.
                    - sell_possible_quantity (float): 매도 가능 수량.
                    - average_purchase_price (float): 평균 매입가.
                    - current_price (float): 현재 가격.
                    - current_value (float): 현재 평가 금액.
                    - current_pnl (float): 현재 손익률.
                    - current_pnl_value (float): 현재 손익 금액.
                    - exchange (str): 거래소 코드.
                    - currency (str): 거래 통화.
                - 데이터프레임 형식 (to_frame=True):
                    - asset_code: 인덱스가 자산 코드인 Pandas DataFrame.
                    - 나머지 필드는 위와 동일.
        """
        positions = self._get_positions()
        if to_frame:
            result = [
                {
                    "asset_code": p["ticker"],
                    "asset_name": p["name"],
                    "quantity": p["qty"],
                    "sell_possible_quantity": p["sell_possible_qty"],
                    "average_purchase_price": p["average_purchase_price"],
                    "current_price": p["current_price"],
                    "current_value": p["current_value"],
                    "current_pnl": p["pnl_rate"],
                    "current_pnl_value": p["pnl"],
                    "exchange": p["exchange"],
                    "currency": p["currency"],
                }
                for p in positions
            ]

            return pd.DataFrame(result).set_index("asset_code")

        else:
            result = [
                OverseasStockPosition(
                    asset_code=p["ticker"],
                    asset_name=p["name"],
                    quantity=p["qty"],
                    sell_possible_quantity=p["sell_possible_qty"],
                    average_purchase_price=p["average_purchase_price"],
                    current_price=p["current_price"],
                    current_value=p["current_value"],
                    current_pnl=p["pnl_rate"],
                    current_pnl_value=p["pnl"],
                    exchange=p["exchange"],
                    currency=p["currency"],
                )
                for p in positions
            ]
            return result

    def get_historical_daily_data_old(
        self,
        ticker: str,
        first_date: dtm.date,
        last_date: dtm.date,
        period: str = "D",
    ) -> pd.DataFrame:
        """
        특정 티커의 일간 데이터를 조회하여 데이터프레임으로 반환합니다.

        Args:
            ticker (str): 조회할 자산의 티커(symbol).
            first_date (datetime.date): 조회를 시작할 첫 번째 날짜 (YYYY-MM-DD). 현지기준 일자.
            last_date (datetime.date): 조회를 마칠 마지막 날짜 (YYYY-MM-DD). 현지 기준 일자.
            period (str, optional): 조회할 데이터의 주기, 기본값은 "D" (일간).

        Returns:
            pd.DataFrame: 조회된 일간 데이터가 포함된 Pandas DataFrame.
                - date (index): 일자 (YYYY-MM-DD 형식).
                - open (float): 시가.
                - high (float): 고가.
                - low (float): 저가.
                - close (float): 종가.
                - volume (int): 거래량.

        Raises:
            ValueError: 주어진 티커가 유효하지 않은 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        rows = []
        fetching = True

        while fetching:
            CallLimiter().wait_limit_rate(90, scope="overseas_daily")

            r = self.stock_api.inquire_daily_chartprice(
                "N",
                ticker,
                first_date,
                last_date,
                period,
            )

            page = []
            next_last_date = None
            for d in r["output2"]:
                row = {
                    "date": d["stck_bsop_date"],
                    "open": float(d["ovrs_nmix_oprc"]),
                    "high": float(d["ovrs_nmix_hgpr"]),
                    "low": float(d["ovrs_nmix_lwpr"]),
                    "close": float(d["ovrs_nmix_prpr"]),
                    "volume": int(d["acml_vol"]),
                }
                page.append(row)
                next_last_date = row["date"]

            if len(page) == 0:
                fetching = False
                break

            rows += page

            last_date = next_last_date - dtm.timedelta(days=1)
            if last_date == first_date:
                fetching = False
                break

        rows.reverse()

        return pd.DataFrame(rows).set_index("date")

    def get_historical_daily_data(
        self,
        ticker: str,
        first_date: dtm.date,
        last_date: dtm.date,
        period: str = "D",
        adjusted_price: bool = True,
    ) -> pd.DataFrame:
        """
        특정 티커의 일간 데이터를 조회하여 데이터프레임으로 반환합니다.

        Args:
            ticker (str): 조회할 자산의 티커(symbol).
            first_date (datetime.date): 조회를 시작할 첫 번째 날짜 (YYYY-MM-DD). 현지기준 일자.
            last_date (datetime.date): 조회를 마칠 마지막 날짜 (YYYY-MM-DD). 현지 기준 일자.
            period (str, optional): 조회할 데이터의 주기, 기본값은 "D" (일간).
            adjusted_price (bool, optional): 수정 종가를 사용할지 여부, 기본값은 True.

        Returns:
            pd.DataFrame: 조회된 일간 데이터가 포함된 Pandas DataFrame.
                - date (index): 일자 (YYYY-MM-DD 형식).
                - open (float): 시가.
                - high (float): 고가.
                - low (float): 저가.
                - close (float): 종가.
                - volume (int): 거래량.
                - value (float): 거래 대금.

        Raises:
            ValueError: 주어진 티커가 유효하지 않은 경우 발생.
        """

        def __period_to_gubn(period):
            # D: 일간, W: 주간, M: 월간
            if period == "D":
                return "0"
            elif period == "W":
                return "1"
            elif period == "M":
                return "2"
            else:
                raise ValueError(f"Unsupported period: {period}")

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        rows = []
        fetching = True
        exchange = self._exchange_to_code(ticker_info["exchange"].loc[ticker])
        search_date = last_date

        gubn = __period_to_gubn(period)
        modp = "1" if adjusted_price else "0"

        while fetching:
            CallLimiter().wait_limit_rate(90, scope="overseas_daily")

            r = self.stock_api.get_dailyprice(exchange, ticker, gubn, modp, search_date.strftime("%Y%m%d"))

            page = []
            next_last_date = None
            for d in r["output2"]:
                row = {
                    "date": d["xymd"],
                    "open": float(d["open"]),
                    "high": float(d["high"]),
                    "low": float(d["low"]),
                    "close": float(d["clos"]),
                    "volume": int(d["tvol"]),
                    "value": d["tamt"],
                }
                page.append(row)
                next_last_date = row["date"]

            if len(page) == 0:
                fetching = False
                break

            rows += page

            search_date = next_last_date - dtm.timedelta(days=1)
            if search_date <= first_date:
                fetching = False
                break

        rows.reverse()

        df = pd.DataFrame(rows).set_index("date")

        return df.loc[first_date:last_date].copy()

    def get_today_minute_data(self, ticker: str) -> pd.DataFrame:
        """
        특정 티커의 시간별 거래 데이터를 조회하여 데이터프레임으로 반환합니다.

        최근 2시간 동안의 데이터만 조회 가능합니다.

        Args:
            ticker (str): 조회할 자산의 티커(symbol).

        Returns:
            pd.DataFrame: 조회된 시간별 거래 데이터가 포함된 Pandas DataFrame.
                - time (datetime): 해당 거래가 발생한 시간 (현지 시간).
                - kr_time (datetime): 한국 시간으로 변환된 시간.
                - open (float): 시가.
                - high (float): 고가.
                - low (float): 저가.
                - close (float): 종가.
                - volume (float): 거래량.
                - value (float): 거래 금액.

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """
        ticker_info = get_ticker_info(ticker)

        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        rows = []

        r = self.stock_api.inquire_time_itemchartprice(
            excd=self._exchange_to_code(ticker_info["exchange"].loc[ticker]),
            symb=ticker,
        )

        output2 = r["output2"]

        for d in output2:
            row = {
                "time": dtm.datetime.combine(d["xymd"], d["xhms"]),
                "kr_time": dtm.datetime.combine(d["kymd"], d["khms"]),
                "open": float(d["open"]),
                "high": float(d["high"]),
                "low": float(d["low"]),
                "close": float(d["last"]),
                "volume": float(d["evol"]),
                "value": float(d["eamt"]),
            }

            rows.append(row)

        rows.reverse()

        return pd.DataFrame(rows).set_index("time")

    def get_price(self, ticker: str) -> pd.DataFrame:
        """
        특정 티커의 현재 가격 정보를 조회하여 데이터프레임으로 반환합니다.

        Args:
            ticker (str): 조회할 자산의 티커(symbol).

        Returns:
            pd.DataFrame: 조회된 가격 정보가 포함된 Pandas DataFrame.
                - ticker (str, index): 자산의 티커.
                - current_price (float): 현재 가격.
                - cum_volume (float): 누적 거래량.
                - cum_value (float): 누적 거래 금액.
                - diff (float): 전일 종가 대비 가격 차이.
                - diff_rate (float): 전일 종가 대비 등락률.
                - sign (int): 등락 기호 (1: 상한, 2: 상승, 3: 보합, 4: 하한, 5: 하락).
                - pclose (float): 전일 종가.
                - pvolume (float): 전일 거래량.
                - ordy (str): 매수 주문 가능 여부 (True/False).

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        r = self.stock_api.get_price(
            self._exchange_to_code(ticker_info["exchange"].loc[ticker]),
            ticker,
        )

        output = r["output"]

        return pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "current_price": output["last"],
                    "cum_volume": output["tvol"],
                    "cum_value": output["tamt"],
                    "diff": output["diff"],
                    "diff_rate": output["rate"],
                    "sign": output["sign"],
                    "pclose": output["base"],
                    "pvolume": output["pvol"],
                    "ordy": output["ordy"],
                }
            ]
        ).set_index("ticker")

    def get_price_detail(self, ticker: str) -> pd.DataFrame:
        """
        특정 티커의 상세 가격 정보를 조회하여 데이터프레임으로 반환합니다.

        Args:
            ticker (str): 조회할 자산의 티커(symbol).

        Returns:
            pd.DataFrame: 티커의 상세 가격 정보가 포함된 데이터프레임.
                - open (float): 시가.
                - high (float): 고가.
                - low (float): 저가.
                - close (float): 종가.
                - pvolume (float): 전일 거래량.
                - pvalue (float): 전일 거래 금액.
                - pclose (float): 전일 종가.
                - market_cap (float): 시가 총액.
                - upper_limit (float): 상한가.
                - lower_limit (float): 하한가.
                - h52_price (float): 52주 최고가.
                - h52_date (str): 52주 최고가 날짜.
                - l52_price (float): 52주 최저가.
                - l52_date (str): 52주 최저가 날짜.
                - per (float): 주가수익비율 (PER).
                - pbr (float): 주가순자산비율 (PBR).
                - eps (float): 주당순이익 (EPS).
                - bps (float): 주당순자산가치 (BPS).
                - shares (int): 발행 주식 수.
                - cap (float): 시가 총액.
                - currency (str): 통화 코드.
                - tick (float): 최소 호가 단위.
                - volume (float): 당일 거래량.
                - value (float): 당일 거래 금액.

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        r = self.stock_api.get_price_detail(
            self._exchange_to_code(ticker_info["exchange"].loc[ticker]),
            ticker,
        )

        output = r["output"]

        result = {
            "ticker": ticker,
            "exchange": ticker_info["exchange"].loc[ticker],
            "open": output["open"],
            "high": output["high"],
            "low": output["low"],
            "close": output["last"],
            "pvolume": output["pvol"],
            "pvalue": output["pamt"],
            "pclose": output["base"],
            "market_cap": output["tomv"],
            "upper_limit": output["uplp"],
            "lower_limit": output["dnlp"],
            "h52_price": output["h52p"],
            "h52_date": output["h52d"],
            "l52_price": output["l52p"],
            "l52_date": output["l52d"],
            "per": output["perx"],
            "pbr": output["pbrx"],
            "eps": output["epsx"],
            "bps": output["bpsx"],
            "shares": output["shar"],
            "cap": output["mcap"],
            "currency": output["curr"],
            "tick": output["e_hogau"],
            "volume": output["tvol"],
            "value": output["tamt"],
        }

        return pd.DataFrame([result]).set_index("ticker")

    def _exchange_to_code(self, exchange: str) -> str:
        if exchange == "NYSE":
            return "NYS"
        elif exchange == "NASD":
            return "NAS"
        elif exchange == "AMEX":
            return "AMS"
        else:
            raise ValueError(f"Unsupported exchange code: {exchange}")

    def create_order(
        self,
        ticker: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType,
        price: Decimal = Decimal("0"),
    ) -> str:
        """
        특정 티커에 대해 매수 또는 매도 주문을 생성합니다.

        Args:
            ticker (str): 주문할 자산의 티커(symbol).
            side (OrderSide): 주문 방향 (매수 또는 매도).
            quantity (int): 주문 수량.
            order_type (OrderType): 주문 유형 (지원되는 주문 유형은 아래와 같음).

                - LIMIT: 지정가 주문.
                - MOO: Market On Open, 시장가 주문 (해외 주식, 매도시에만 가능).
                - LOO: Limit On Open, 개장 시 지정가 주문 (해외 주식).
                - MOC: Market On Close, 종가 기준 시장가 주문 (해외 주식, 매도시에만 가능).
                - LOC: Limit On Close, 종가 기준 지정가 주문 (해외 주식).
            price (Decimal): 주문 가격 (지정가 주문일 경우).

        Returns:
            str: 주문 번호 (Order NO).

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        ovrs_excg_cd = ticker_info["exchange"].loc[ticker]

        r = self.stock_api.order(
            self.account_no,
            self.account_product_code,
            ovrs_excg_cd,
            ticker,
            quantity,
            price,
            "00" if side == OrderSide.SELL else "01",
            self._order_type_to_code(order_type),
        )

        output = r["output"]
        return output["ODNO"]

    def _code_to_order_type(self, code: str) -> OrderType:
        if code == "00":
            return OrderType.LIMIT
        elif code == "31":
            return OrderType.MOO
        elif code == "32":
            return OrderType.LOO
        elif code == "33":
            return OrderType.MOC
        elif code == "34":
            return OrderType.LOC
        else:
            raise ValueError(f"Unsupported order type code: {code}")

    def _order_type_to_code(self, order_type: OrderType) -> str:
        if order_type == OrderType.LIMIT:
            return "00"
        elif order_type == OrderType.MOO:
            return "31"
        elif order_type == OrderType.LOO:
            return "32"
        elif order_type == OrderType.MOC:
            return "33"
        elif order_type == OrderType.LOC:
            return "34"
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

    def update_order(
        self,
        ticker: str,
        org_order_no: str,
        price: Decimal,
        quantity: int,
    ) -> str:
        """
        기존 주문을 수정합니다.

        Args:
            ticker (str): 수정할 자산의 티커(symbol).
            org_order_no (str): 수정할 기존 주문의 주문 번호.
            price (Decimal): 수정된 주문 가격.
            quantity (int): 수정된 주문 수량.

        Returns:
            str: 수정된 주문의 새로운 주문 번호 (Order ID).

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        ovrs_excg_cd = ticker_info["exchange"].loc[ticker]

        r = self.stock_api.order_rvsecncl(
            self.account_no,
            self.account_product_code,
            ovrs_excg_cd,
            ticker,
            org_order_no,
            "01",
            quantity,
            price,
        )
        output = r["output"]
        return output["ODNO"]

    def cancel_order(
        self,
        ticker: str,
        order_no: str,
        quantity: int,
    ) -> str:
        """
        기존 주문을 취소합니다.

        Args:
            ticker (str): 취소할 자산의 티커(symbol).
            order_no (str): 취소할 주문의 주문 번호.
            quantity (int): 취소할 주문 수량.

        Returns:
            str: 취소된 주문의 주문 번호 (Order ID).

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        ovrs_excg_cd = ticker_info["exchange"].loc[ticker]

        self.stock_api.order_rvsecncl(
            self.account_no,
            self.account_product_code,
            ovrs_excg_cd,
            ticker,
            order_no,
            "02",
            quantity,
            Decimal("0"),
        )

    def get_pending_orders(self, to_frame: bool = False) -> List[OverseasStockOrder] | pd.DataFrame:
        """
        대기 중인 주문들을 조회하여 리스트 또는 데이터프레임 형식으로 반환합니다.

        Args:
            to_frame (bool, optional): True일 경우 Pandas DataFrame으로 반환, False일 경우 리스트 형식의 OverseasStockOrder 객체들로 반환. 기본값은 False.

        Returns:
            List[OverseasStockOrder] | pd.DataFrame: 대기 중인 주문 정보 리스트 또는 DataFrame.
                - 리스트 형식 (OverseasStockOrder 객체들):
                    - order_no (str): 주문 번호.
                    - asset_code (str): 자산 코드 (티커).
                    - side (OrderSide): 매수(BUY) 또는 매도(SELL).
                    - price (Decimal): 주문 가격.
                    - quantity (int): 주문 수량.
                    - filled_quantity (int): 체결된 수량.
                    - pending_quantity (int): 대기 중인 수량.
                    - order_time (datetime): 주문 시간.
                    - filled_price (Decimal): 체결 가격.
                    - current_price (Decimal): 현재 가격 (초기값 None).
                    - is_pending (bool): 주문 대기 여부.
                    - org_order_no (str): 원래 주문 번호 (수정/취소 주문의 경우).
                    - order_type (str): 주문 유형 (초기값 None).
                    - req_type (str): 주문 요청 유형 (정정/취소 등).
                - 데이터프레임 형식 (to_frame=True):
                    - 주문 번호(order_no)를 인덱스로 한 Pandas DataFrame.
                    - 나머지 필드는 위와 동일하며, 가격과 수량은 숫자 형식으로 변환됨.

        Raises:
            ValueError: API 호출 중 문제가 발생할 경우 발생.
        """
        r = self.stock_api.inquire_ccnl(
            self.account_no,
            self.account_product_code,
            dtm.date.today(),
            dtm.date.today(),
            "NASD",
            "%",
            "00",
            "02",
        )
        output = r["output"]
        result = []
        for d in output:
            order_kr_time = dtm.datetime.combine(d["dmst_ord_dt"], d["ord_tmd"], tzinfo=self.kst)
            order_time = order_kr_time.astimezone(self.nyt)

            order = OverseasStockOrder(
                order_no=d["odno"],
                asset_code=d["pdno"],
                side=OrderSide.BUY if d["sll_buy_dvsn_cd"] == "02" else OrderSide.SELL,
                price=Decimal(d["ft_ord_unpr3"]),
                quantity=d["ft_ord_qty"],
                filled_quantity=d["ft_ccld_qty"],
                pending_quantity=d["nccs_qty"],
                order_time=order_time,
                order_kr_time=order_kr_time,
                filled_price=d["ft_ccld_unpr3"],
                current_price=self._get_cached_price(d["pdno"]),
                is_pending=d["nccs_qty"] != 0,
                org_order_no=d["orgn_odno"],
                order_type=None,
                req_type=self._code_to_order_request_type(d["rvse_cncl_dvsn"]),
                exchange=d["ovrs_excg_cd"],
                currency=d["tr_crcy_cd"],
            )

            result.append(order)

        if to_frame:
            rows = []

            for order in result:
                d = asdict(order)
                d["price"] = float(d["price"])
                d["filled_price"] = float(d["filled_price"])
                d["current_price"] = float(d["current_price"])
                d["side"] = "BUY" if d["side"] == OrderSide.BUY else "SELL"
                d["req_type"] = self._request_type_to_str(d["req_type"])

                rows.append(d)

            return (
                pd.DataFrame(rows)
                .astype(
                    {
                        "org_order_no": "string",
                        "order_no": "string",
                    }
                )
                .set_index("order_no")
            )

        else:
            return result

    def get_today_order_history(self, target_date: Optional[dtm.date] = None, to_frame: bool = False) -> List[OverseasStockOrder] | pd.DataFrame:
        """
        현지 기준 오늘의 주문 내역을 조회하여 리스트 또는 데이터프레임 형식으로 반환합니다.

        Args:
            target_date (dtm.date, optional): 조회할 현지 기준 날짜. 기본값은 None (오늘).
            to_frame (bool, optional): True일 경우 Pandas DataFrame으로 반환, False일 경우 리스트 형식의 OverseasStockOrder 객체들로 반환. 기본값은 False.

        Returns:
            List[OverseasStockOrder] | pd.DataFrame: 현지 기준 오늘의 주문 내역 리스트 또는 DataFrame.
                - 리스트 형식 (OverseasStockOrder 객체들):
                    - order_no (str): 주문 번호.
                    - asset_code (str): 자산 코드 (티커).
                    - side (OrderSide): 매수(BUY) 또는 매도(SELL).
                    - price (Decimal): 주문 가격.
                    - quantity (int): 주문 수량.
                    - filled_quantity (int): 체결된 수량.
                    - pending_quantity (int): 대기 중인 수량.
                    - order_time (datetime): 주문 시간. 현지 기준.
                    - order_kr_time (datetime): 주문 시간. 한국 기준.
                    - filled_price (Decimal): 체결 가격.
                    - current_price (Decimal): 현재 가격.
                    - is_pending (bool): 주문 대기 여부.
                    - org_order_no (str): 원래 주문 번호 (수정/취소 주문의 경우).
                    - order_type (str): 주문 유형 (초기값 None).
                    - req_type (str): 주문 요청 유형 (정정/취소 등).
                    - exchange (str): 거래소 코드.
                    - currency (str): 거래 통화 코드.
                - 데이터프레임 형식 (to_frame=True):
                    - 주문 번호(order_no)를 인덱스로 한 Pandas DataFrame.
                    - 나머지 필드는 위와 동일하며, 가격과 수량은 숫자 형식으로 변환됨.

        Raises:
            ValueError: API 호출 중 문제가 발생할 경우 발생.
        """
        if target_date is None:
            tzinfo = ZoneInfo("America/New_York")
            from_date = dtm.datetime.now(tzinfo).date()
            to_date = from_date
        else:
            from_date = target_date
            to_date = target_date

        return self.get_order_history(from_date, to_date, to_frame)

    def get_order_history(
        self,
        from_date: dtm.date,
        to_date: dtm.date,
        to_frame: bool = False,
    ) -> List[OverseasStockOrder] | pd.DataFrame:
        """
        주문 내역을 조회하여 리스트 또는 데이터프레임 형식으로 반환합니다.

        Args:
            from_date (dtm.date): 조회를 시작할 날짜. (현지 기준)
            to_date (dtm.date): 조회를 마칠 날짜. (현지 기준)
            to_frame (bool, optional): True일 경우 Pandas DataFrame으로 반환, False일 경우 리스트 형식의 OverseasStockOrder 객체들로 반환. 기본값은 False.

        Returns:
            List[OverseasStockOrder] | pd.DataFrame: 오늘의 주문 내역 리스트 또는 DataFrame.
                - 리스트 형식 (OverseasStockOrder 객체들):
                    - order_no (str): 주문 번호.
                    - asset_code (str): 자산 코드 (티커).
                    - side (OrderSide): 매수(BUY) 또는 매도(SELL).
                    - price (Decimal): 주문 가격.
                    - quantity (int): 주문 수량.
                    - filled_quantity (int): 체결된 수량.
                    - pending_quantity (int): 대기 중인 수량.
                    - order_time (datetime): 주문 시간 (현지 기준).
                    - order_kr_time (datetime): 주문 시간 (한국 기준).
                    - filled_price (Decimal): 체결 가격.
                    - current_price (Decimal): 현재 가격.
                    - is_pending (bool): 주문 대기 여부.
                    - org_order_no (str): 원래 주문 번호 (수정/취소 주문의 경우).
                    - order_type (str): 주문 유형 (초기값 None).
                    - req_type (str): 주문 요청 유형 (정정/취소 등).
                    - exchange (str): 거래소 코드.
                    - currency (str): 거래 통화 코드.
                - 데이터프레임 형식 (to_frame=True):
                    - 주문 번호(order_no)를 인덱스로 한 Pandas DataFrame.
                    - 나머지 필드는 위와 동일하며, 가격과 수량은 숫자 형식으로 변환됨.

        Raises:
            ValueError: API 호출 중 문제가 발생할 경우 발생.
        """

        result = []
        fetching = True
        ctx_area_fk200 = ""
        ctx_area_nk200 = ""
        tr_cont = ""

        while fetching:
            r = self.stock_api.inquire_ccnl(
                self.account_no,
                self.account_product_code,
                from_date,
                to_date,
                "NASD",
                "%",
                "00",
                "00",
                ctx_area_fk200=ctx_area_fk200,
                ctx_area_nk200=ctx_area_nk200,
                tr_cont=tr_cont,
            )
            output = r["output"]

            for d in output:
                order_kr_time = dtm.datetime.combine(d["dmst_ord_dt"], d["ord_tmd"], tzinfo=self.kst)
                order_time = order_kr_time.astimezone(self.nyt)

                order = OverseasStockOrder(
                    order_no=d["odno"],
                    asset_code=d["pdno"],
                    side=OrderSide.BUY if d["sll_buy_dvsn_cd"] == "02" else OrderSide.SELL,
                    price=Decimal(d["ft_ord_unpr3"]),
                    quantity=d["ft_ord_qty"],
                    filled_quantity=d["ft_ccld_qty"],
                    pending_quantity=d["nccs_qty"],
                    order_time=order_time,
                    order_kr_time=order_kr_time,
                    filled_price=d["ft_ccld_unpr3"],
                    current_price=self._get_cached_price(d["pdno"]),
                    is_pending=d["nccs_qty"] != 0,
                    org_order_no=d["orgn_odno"],
                    order_type=None,
                    req_type=self._code_to_order_request_type(d["rvse_cncl_dvsn"]),
                    exchange=d["ovrs_excg_cd"],
                    currency=d["tr_crcy_cd"],
                )
                result.append(order)

            if r["tr_cont"] in ["F", "M"]:
                ctx_area_fk200 = r["ctx_area_fk200"]
                ctx_area_nk200 = r["ctx_area_nk200"]
                tr_cont = "N"
            else:
                fetching = False

        if to_frame:
            rows = []

            for order in result:
                d = asdict(order)
                d["price"] = float(d["price"])
                d["filled_price"] = float(d["filled_price"])
                d["current_price"] = float(d["current_price"])
                d["side"] = "BUY" if d["side"] == OrderSide.BUY else "SELL"
                d["req_type"] = self._request_type_to_str(d["req_type"])

                rows.append(d)

            return (
                pd.DataFrame(rows)
                .astype(
                    {
                        "org_order_no": "string",
                        "order_no": "string",
                    }
                )
                .set_index("order_no")
            )

        else:
            return result

    def _code_to_order_request_type(self, code: str) -> OrderRequestType:
        if code == "00":
            return OrderRequestType.NEW
        elif code == "01":
            return OrderRequestType.MODIFY
        elif code == "02":
            return OrderRequestType.CANCEL
        else:
            raise ValueError(f"Unknown order request type code: {code}")

    def _request_type_to_str(self, req_type: OrderRequestType) -> str:
        if req_type == OrderRequestType.NEW:
            return "NEW"
        elif req_type == OrderRequestType.MODIFY:
            return "MODIFY"
        elif req_type == OrderRequestType.CANCEL:
            return "CANCEL"
        else:
            raise ValueError(f"Unknown order request type: {req_type}")

    @ttl_cache(maxsize=100, ttl=1)
    def _get_cached_price(self, ticker: str) -> Decimal | None:
        df = self.get_price(ticker)
        if not df.empty:
            return df.loc[ticker, "current_price"]
        else:
            return None

    def schedule_order(
        self,
        ticker: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType,
        price: Decimal,
    ) -> str:
        """
        주식 예약 주문을 생성합니다. 지정가 주문 및 MOO(장 개시 시장가) 주문이 지원됩니다.

        Args:
            ticker (str): 예약 주문할 주식의 티커(symbol).
            side (OrderSide): 매도 또는 매수 방향 (OrderSide.SELL 또는 OrderSide.BUY).
            quantity (int): 주문 수량.
            order_type (OrderType): 주문 유형 (지원되는 주문 유형: OrderType.LIMIT, OrderType.MOO).
            price (Decimal): 지정가 주문일 경우의 가격.

        Returns:
            str: 생성된 예약 주문의 주문 번호.

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 지원되지 않는 거래소인 경우.
            ValueError: 지원되지 않는 주문 유형일 경우.
            ValueError: MOO(장 개시 시장가) 주문이 매수 주문일 경우 (MOO는 매도 주문에서만 사용 가능).
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        exchange = ticker_info["exchange"].loc[ticker]
        if exchange not in self.get_supported_exchange_codes():
            raise ValueError(f"Unsupported exchange: {exchange}")

        if order_type not in [OrderType.LIMIT, OrderType.MOO]:
            raise ValueError(f"Unsupported order type: {order_type}")

        if order_type == OrderType.MOO and side == OrderSide.BUY:
            raise ValueError("Market On Open order is only available for sell orders")

        r = self.stock_api.order_resv(
            self.account_no,
            self.account_product_code,
            ticker,
            exchange,
            quantity,
            price,
            "01" if side == OrderSide.SELL else "02",
            self._order_type_to_code(order_type),
        )

        return {
            "order_no": r["output"]["ODNO"],
            "date": dtm.datetime.now(self.nyt).strftime("%Y%m%d"),
        }

    def cancel_scheduled_order(self, org_order_no: str, reservation_date: dtm.date):
        """
        주식 예약 주문을 취소합니다.

        Args:
            org_order_no (str): 취소할 예약 주문의 주문 번호.
            reservation_date (datetime.date): 예약 주문 접수 일자. 현지기준.

        Returns:
            str: 취소된 예약 주문 번호 (OVRS_RSVN_ODNO).

        Raises:
            ValueError: API 호출 중 문제가 발생한 경우.
        """

        r = self.stock_api.order_resv_ccnl(
            self.account_no,
            self.account_product_code,
            reservation_date,
            org_order_no,
        )

        return r["output"]["OVRS_RSVN_ODNO"]

    def get_scheduled_orders(
        self,
        start_date: Optional[dtm.date] = None,
        end_date: Optional[dtm.date] = None,
        include_cancelled: bool = False,
        to_frame: bool = False,
    ) -> List[dict] | pd.DataFrame:
        """
        지정된 기간 동안의 예약 주문 목록을 조회합니다.

        Args:
            start_date (datetime.date, optional): 현지 기준 조회할 시작 일자. 기본값은 당일.
            end_date (datetime.date, optional): 현지 기준 조회할 종료 일자. 기본값은 당일.
            include_cancelled (bool, optional): 취소된 예약 주문을 포함할지 여부. 기본값은 False.
            to_frame (bool, optional): True일 경우 Pandas DataFrame으로 반환, False일 경우 리스트 형식의 dict 객체들로 반환. 기본값은 False.

        Returns:
            List[dict]: 예약 주문 목록.
                각 사전에는 다음과 같은 정보가 포함됩니다:

                - is_cancelled (str): 주문 취소 여부.
                - reservation_date (str): 현지 기준 예약 주문 접수 일자 (YYYYMMDD).
                - order_no (str): 해외 예약 주문 번호.
                - asset_code (str): 자산 코드 (티커).
                - order_date (str): 주문 일자 (YYYYMMDD).
                - side (str): 매수/매도 구분 코드.
                - side_name (str): 매수/매도 구분 명칭.
                - ticker (str): 상품 번호 (티커).
                - name (str): 상품명.
                - quantity (str): 주문 수량.
                - price (str): 주문 단가.
                - filled_quantity (str): 체결 수량.
                - filled_price (str): 체결 단가.
                - fail_reason (str): 주문 미체결 사유 (존재할 경우).

        Raises:
            ValueError: API 호출 중 문제가 발생한 경우.
        """

        if start_date is None:
            start_date = dtm.datetime.now(self.nyt).date()
        if end_date is None:
            end_date = dtm.datetime.now(self.nyt).date()

        r = self.stock_api.order_resv_list(
            self.account_no,
            self.account_product_code,
            start_date,
            end_date,
        )

        result = []
        for d in r["output"]:
            if not include_cancelled and d["cncl_yn"] is True:
                continue

            order = {
                "is_cancelled": d["cncl_yn"],
                "reservation_date": d["rsvn_ord_rcit_dt"],
                "order_no": d["ovrs_rsvn_odno"],
                "order_date": d["ord_dt"],
                "side": OrderSide.BUY if d["sll_buy_dvsn_cd"] == "02" else OrderSide.SELL,
                "side_name": d["sll_buy_dvsn_cd_name"],
                "ticker": d["pdno"],
                "name": d["prdt_name"],
                "quantity": d["ft_ord_qty"],
                "price": d["ft_ord_unpr3"],
                "filled_quantity": d["ft_ccld_qty"],
                "filled_price": d["ft_ccld_unpr3"],
                "fail_reason": d["nprc_rson_text"],
            }

            result.append(order)

        if to_frame:
            for row in result:
                row["side"] = "BUY" if row["side"] == OrderSide.BUY else "SELL"
                row["price"] = float(row["price"]) if row["price"] is not None else None
                row["filled_price"] = float(row["filled_price"]) if row["filled_price"] is not None else None

            df = pd.DataFrame(result)
            if not df.empty:
                df.set_index("order_no", inplace=True)

            return df

        else:
            return result

    def get_orderbook(self, ticker: str) -> Dict:
        """
        특정 티커의 호가/잔량 정보를 조회하여 반환합니다.

        Args:
            ticker (str): 조회할 자산의 티커(symbol).

        Returns:
            dict: 호가 정보가 포함된 사전.
                - total_bid_volume (int): 총 매수 잔량.
                - total_ask_volume (int): 총 매도 잔량.
                - ask_price (Decimal): 1차 매도 호가 가격.
                - ask_volume (int): 1차 매도 호가 잔량.
                - bid_price (Decimal): 1차 매수 호가 가격.
                - bid_volume (int): 1차 매수 호가 잔량.
                - time (dtm.datetime): 현지 기준 호가 정보 조회 시간.
                - bids (list): 매수 호가 목록 (각 항목은 price와 volume을 포함하는 dict).
                - asks (list): 매도 호가 목록 (각 항목은 price과 volume을 포함하는 dict).

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """

        ticker_info = get_ticker_info(ticker)
        if ticker_info is None:
            raise ValueError(f"Ticker {ticker} not found")

        exchange = ticker_info["exchange"].loc[ticker]

        r = self.stock_api.inquire_asking_price(
            self._exchange_to_code(exchange),
            ticker,
        )

        o1 = r["output1"]
        o2 = r["output2"]

        result = {
            "total_bid_volume": o1["bvol"],
            "total_ask_volume": o1["avol"],
            "ask_price": o2["pask1"],
            "ask_volume": o2["vask1"],
            "bid_price": o2["pbid1"],
            "bid_volume": o2["vbid1"],
            "time": dtm.datetime.strptime(o1["dymd"] + o1["dhms"], "%Y%m%d%H%M%S").astimezone(self.nyt),
            "bids": [{"price": o2[f"pbid{i}"], "volume": o2[f"vbid{i}"]} for i in range(1, 11)],
            "asks": [{"price": o2[f"pask{i}"], "volume": o2[f"vask{i}"]} for i in range(1, 11)],
        }

        return result
