import asyncio
import datetime as dtm
from decimal import Decimal
from typing import AsyncGenerator, Dict, List, Optional

import pandas as pd

from pyqqq.brokerage.kis.domestic_stock import KISDomesticStock
from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.data.realtime import get_all_last_trades
from pyqqq.datatypes import *
from pyqqq.utils.limiter import CallLimiter
from pyqqq.utils.logger import get_logger
from pyqqq.utils.market_schedule import get_market_schedule, is_full_day_closed
from pyqqq.utils.mock_api import with_mock


class KISStockPosition(StockPosition):
    pass


class KISStockOrder(StockOrder):
    pass


class KISSimpleDomesticStock:
    """
    한국투자증권 국내 주식 API 사용하여 주식 거래를 하기 위한 클래스입니다.

    기존 KISDomesticStock 클래스를 감싸고, 간단한 주문/조회 기능을 제공합니다.

    Attributes:
        auth (KISAuth): 인증 정보
        account_no (str): 계좌 번호
        account_product_code (str): 계좌 상품 코드
        hts_id (Optional[str]): HTS ID
        corp_data (Optional[dict]): 기업 고객의 경우 추가로 필요한 정보를 담고 있는 객체
    """

    def __init__(
        self,
        auth: KISAuth,
        account_no: str,
        account_product_code: str,
        hts_id: Optional[str] = None,
        corp_data: Optional[dict] = None,
    ):
        self.account_no = account_no
        self.account_product_code = account_product_code
        self.stock_api = KISDomesticStock(auth, corp_data)
        self.hts_id = hts_id
        self.logger = get_logger(__name__ + ".KISSimpleDomesticStock")

    def get_account(self) -> dict:
        """
        계좌 정보를 조회합니다.

        Returns:
            dict: 계좌 정보

            - total_balance (int): 총 평가 금액
            - purchase_amount (int): 매입 금액
            - evaluated_amount (int): 평가 금액
            - pnl_amount (int): 손익 금액
            - pnl_rate (Decimal): 손익률
        """
        r = self.stock_api.inquire_balance(self.account_no, self.account_product_code, "01")
        data = r["output2"][0]

        purchase_amount = int(data["pchs_amt_smtl_amt"])
        pnl_amount = int(data["evlu_pfls_smtl_amt"])
        pnl_rate = Decimal(pnl_amount / purchase_amount) * 100 if purchase_amount != 0 else Decimal(0)

        result = {
            "total_balance": int(data["tot_evlu_amt"]),
            "purchase_amount": purchase_amount,
            "evaluated_amount": int(data["evlu_amt_smtl_amt"]),
            "pnl_amount": pnl_amount,
            "pnl_rate": pnl_rate,
        }
        return result

    def get_possible_quantity(
        self,
        asset_code: str,
        order_type: OrderType = OrderType.MARKET,
        price: int = 0,
    ) -> dict:
        """
        주문 가능 수량을 조회합니다.

        Args:
            asset_code (str): 종목 코드
            order_type (OrderType): 주문 유형
            price (int): 주문 가격 (지정가 주문일 경우에만 필요)

        Returns:
            dict: 주문 가능 수량 정보

            - investable_cash (int): 주문 가능 현금
            - reusable_amount (int): 재사용 가능 금액
            - price (int): 계산 기준 단가
            - quantity (int): 주문 가능 수량
            - amount (int): 주문 시 소요 금액
        """

        # XXX MID_POINT, STOP_LIMIT 의 경우, 홈페이지에는 안내가 없으나 API 호출은 가능
        def __get_order_type_code():
            if order_type == OrderType.MARKET:
                return "01"
            elif order_type == OrderType.LIMIT:
                return "00"
            elif order_type == OrderType.LIMIT_IOC:
                return "11"
            elif order_type == OrderType.LIMIT_FOK:
                return "12"
            elif order_type == OrderType.MARKET_IOC:
                return "13"
            elif order_type == OrderType.MARKET_FOK:
                return "14"
            elif order_type == OrderType.MID_POINT:
                return "21"
            elif order_type == OrderType.MID_POINT_IOC:
                return "23"
            elif order_type == OrderType.MID_POINT_FOK:
                return "24"
            elif order_type == OrderType.STOP_LIMIT:
                return "22"
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        resp = self.stock_api.inquire_psbl_order(
            self.account_no,
            self.account_product_code,
            asset_code,
            __get_order_type_code(),
            price,
        )

        data = resp["output"]
        result = {
            "investable_cash": data["ord_psbl_cash"],
            "reusable_amount": data["ruse_psbl_amt"],
            "price": data["psbl_qty_calc_unpr"],
            "quantity": data["max_buy_qty"],
            "amount": data["max_buy_amt"],
        }
        return result

    def get_positions(self) -> List[StockPosition]:
        """
        보유 종목을 조회합니다.

        Returns:
            List[StockPosition]: 보유 종목 정보 리스트
        """

        fetching = True
        ctx_area_fk100 = ""
        ctx_area_nk100 = ""
        tr_cont = ""

        result = []

        while fetching:
            r = self.stock_api.inquire_balance(
                self.account_no,
                self.account_product_code,
                "02",
                "X",
                tr_cont=tr_cont,
                ctx_area_fk100=ctx_area_fk100,
                ctx_area_nk100=ctx_area_nk100,
            )

            for el in r["output1"]:
                position = StockPosition(
                    asset_code=el["pdno"],
                    asset_name=el["prdt_name"],
                    quantity=int(el["hldg_qty"]),
                    sell_possible_quantity=int(el["ord_psbl_qty"]),
                    average_purchase_price=Decimal(el["pchs_avg_pric"]),
                    current_price=int(el["prpr"]),
                    current_value=int(el["evlu_amt"]),
                    current_pnl=Decimal(el["evlu_pfls_rt"]),
                    current_pnl_value=el["evlu_pfls_amt"],
                )

                if position.quantity > 0:
                    result.append(position)

            if r["tr_cont"] in ["F", "M"]:
                tr_cont = "N"
                ctx_area_fk100 = r["ctx_area_fk100"]
                ctx_area_nk100 = r["ctx_area_nk100"]
            else:
                fetching = False

        return result

    def _get_data_exchange(self, data_exchange: DataExchange) -> str:
        if data_exchange == DataExchange.KRX:
            return "J"
        elif data_exchange == DataExchange.NXT:
            return "NX"
        elif data_exchange == DataExchange.UN:
            return "UN"
        else:
            raise ValueError("지원하지 않는 거래소입니다.")

    def get_historical_daily_data(
        self,
        asset_code: str,
        first_date: dtm.date,
        last_date: dtm.date,
        adjusted_price: bool = True,
        data_exchange: DataExchange = DataExchange.KRX,
    ) -> pd.DataFrame:
        """
        일봉 데이터 검색

        Note:
            - 두 거래소에서 공통으로 거래정지된 종목의 시가/고가/저가/종가는 모두 동일하며, 그 외 값은 모두 0 입니다.
            - NXT 매매체결 종목이 아니거나, NXT 거래소에서 거래가 불가능한 종목을 DataExchange.NXT 또는 DataExchange.UN으로 조회하면, 모든 값은 0 입니다.
            - 조회 기간 중 휴장일은 포함되지 않습니다.

        Args:
            asset_code(str): 종목코드
            first_date(datetime.date): 조회 시작일자
            last_date(datetime.date): 조회 종료일자
            adjusted_price(bool): 수정 주가 여부
            data_exchange(DataExchange): 데이터 거래소

        Returns:
            pd.DataFrame: 일봉 데이터
        """
        assert first_date <= last_date, "last_date는 first_date와 같거나, 이후 날짜여야 합니다"
        assert last_date <= dtm.date.today(), "last_date는 오늘과 같거나 이전이어야 합니다."

        max_days_per_request = 100
        total_days = (last_date - first_date).days

        result = []

        for i in range(0, total_days + 1, max_days_per_request + 1):
            search_start = first_date + dtm.timedelta(days=i)
            search_end = min(first_date + dtm.timedelta(days=i + max_days_per_request), last_date)

            CallLimiter().wait_limit_rate(20, scope="kis/inquire_daily_itemchartprice")
            r = self.stock_api.inquire_daily_itemchartprice(
                asset_code,
                search_start,
                search_end,
                fid_period_div_code="D",
                fid_cond_mrkt_div_code=self._get_data_exchange(data_exchange),
                fid_org_adj_prc="0" if adjusted_price else "1",
            )

            chunk = []
            for item in r["output2"]:
                if not item:
                    continue

                chunk.append(
                    {
                        "date": item["stck_bsop_date"],
                        "open": item["stck_oprc"],
                        "high": item["stck_hgpr"],
                        "low": item["stck_lwpr"],
                        "close": item["stck_clpr"],
                        "volume": item["acml_vol"],
                        "value": item["acml_tr_pbmn"],
                    }
                )
            result.extend(chunk)

        df = pd.DataFrame(result, columns=["date", "open", "high", "low", "close", "volume", "value"])
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        # 조회기간 중 데이터가 없는 날짜는 0 으로 채움
        dates = pd.date_range(start=first_date, end=last_date, freq="B")
        if len(dates) != len(df):
            dates = [date for date in dates if not is_full_day_closed(date)]
            df = df.reindex(dates, fill_value=0)

        df = df.sort_index(ascending=False)
        return df

    def get_today_minute_data(
        self,
        asset_code: str,
        data_exchange: DataExchange = DataExchange.KRX,
    ) -> pd.DataFrame:
        """
        분봉 데이터 검색

        Note:
            - 시간외 종가, 시간외 단일가 데이터는 포함되어 있지 않습니다.
            - 두 거래소에서 공통으로 거래정지된 종목의 시가/고가/저가/종가는 모두 동일하며, 그 외 값은 모두 0 입니다.
            - NXT 매매체결 종목이 아니거나, NXT 거래소에서 거래가 불가능한 종목을 DataExchange.NXT 또는 DataExchange.UN으로 조회하면, 모든 값은 0 입니다.
            - 휴장일에는 빈 DataFrame을 반환합니다.

        Args:
            asset_code(str): 종목코드
            data_exchange(DataExchange): 데이터 거래소

        Returns:
            pd.DataFrame: 분봉 데이터 (시간의 역순)
        """

        def _create_minute_dataframe(data: list = None) -> pd.DataFrame:
            """
            분봉 데이터를 위한 DataFrame을 생성합니다.

            Args:
                data (list, optional): 분봉 데이터 리스트. None이면 빈 DataFrame을 반환합니다.

            Returns:
                pd.DataFrame: 분봉 데이터 DataFrame
            """
            if data is None:
                data = []

            df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume", "value", "cum_volume", "cum_value"])
            df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S")
            df.set_index("time", inplace=True)
            return df

        request_datetime = dtm.datetime.now()
        request_time = request_datetime.replace(second=0, microsecond=0)
        result = []
        schedule = get_market_schedule(dtm.date.today(), exchange="KRX" if data_exchange == DataExchange.KRX else "NXT")

        if schedule.full_day_closed:
            return _create_minute_dataframe()

        # KRX 거래소에서 15:30 ~ 17:00 시간대에 API 호출하면 15:30분 데이터는 존재하지 않고, 해당 데이터가 호출시점(마지막) 인덱스에 존재 한다.
        # 이러한 문제를 피하기위해 request_time을 장 종료 시간으로 설정한다.
        requires_volume_correction = False
        if request_time.time() > schedule.close_time:
            request_time = request_datetime.replace(hour=schedule.close_time.hour, minute=schedule.close_time.minute)

            if data_exchange == DataExchange.KRX:
                requires_volume_correction = True

        while True:
            CallLimiter().wait_limit_rate(20, scope="kis/inquire_time_itemchartprice")

            r = self.stock_api.inquire_time_itemchartprice(
                asset_code,
                request_time.time(),
                fid_cond_mrkt_div_code=self._get_data_exchange(data_exchange),
                fid_pw_data_incu_yn="N",
            )
            output = r["output2"]
            if len(output) == 0:
                break

            for item in output:
                if not item:
                    continue

                result.append(
                    {
                        "time": dtm.datetime.combine(item["stck_bsop_date"], item["stck_cntg_hour"]),
                        "open": item["stck_oprc"],
                        "high": item["stck_hgpr"],
                        "low": item["stck_lwpr"],
                        "close": item["stck_prpr"],
                        "volume": item["cntg_vol"],
                        "cum_value": item["acml_tr_pbmn"],
                    }
                )

            last_item_time = result[-1]["time"]
            request_time = last_item_time - dtm.timedelta(minutes=1)
            if request_time.time() < schedule.open_time:
                break

        # KRX 거래소에서 17시 이후에 API 호출하면 거래량이 2배로 보이는 문제가 있다. 장 마감 이후에는 거래량 검사를 진행한다.
        if requires_volume_correction:
            close = result[0].get("close")
            volume = (result[0].get("cum_value") - result[1].get("cum_value")) / close
            if volume != result[0].get("volume"):
                result[0]["volume"] = int(volume)

        # 거래대금, 누적거래량 계산
        prev_cum_value = None
        prev_cum_volume = None

        for i in range(len(result)):
            idx = len(result) - i - 1
            curr = result[idx]

            if prev_cum_value is None:
                curr["value"] = curr["cum_value"]
            else:
                curr["value"] = curr["cum_value"] - prev_cum_value

            if prev_cum_volume is None:
                curr["cum_volume"] = curr["volume"]
            else:
                curr["cum_volume"] = curr["volume"] + prev_cum_volume

            prev_cum_value = curr["cum_value"]
            prev_cum_volume = curr["cum_volume"]

        return _create_minute_dataframe(result)

    def get_price(
        self,
        asset_code: str,
        data_exchange: DataExchange = DataExchange.KRX,
    ) -> dict:
        """
        주식 현재 가격 조회

        Args:
            asset_code(str): 종목코드
            data_exchange(DataExchange): 데이터 거래소

        Returns:
            dict: 현재 가격 정보

            - code (str): 종목 코드
            - current_price (int): 현재 가격
            - volume (int): 거래량
            - open_price (int): 시가
            - high_price (int): 고가
            - low_price (int): 저가
            - max_price (int): 상한가
            - min_price (int): 하한가
            - diff (int): 전일대비
            - diff_rate (float): 전일대비율
        """
        r = self.stock_api.get_price(asset_code, self._get_data_exchange(data_exchange))

        data = r["output"]
        result = {
            "code": asset_code,
            "current_price": data["stck_prpr"],
            "volume": data["acml_vol"],
            "open_price": data["stck_oprc"],
            "high_price": data["stck_hgpr"],
            "low_price": data["stck_lwpr"],
            "max_price": data["stck_mxpr"],
            "min_price": data["stck_llam"],
            "diff": data["prdy_vrss"],
            "diff_rate": float(data["prdy_ctrt"]),
        }

        return result

    def get_price_for_multiple_stock(self, asset_codes: List[str]) -> pd.DataFrame:
        """
        여러 종목의 현재 가격 조회

        Args:
            asset_codes(List[str]): 종목 코드 리스트

        Returns:
            pd.DataFrame: 현재 가격 정보

            - code (str): 종목 코드
            - current_price (int): 현재 가격
            - volume (int): 거래량
            - open_price (int): 시가
            - high_price (int): 고가
            - low_price (int): 저가
            - diff (int): 전일대비
            - diff_rate (float): 전일대비율
        """
        r = get_all_last_trades()
        result = []

        for item in r:
            if item["shcode"] in asset_codes:
                result.append(
                    {
                        "code": item["shcode"],
                        "current_price": item["price"],
                        "volume": item["volume"],
                        "open_price": item["open"],
                        "high_price": item["high"],
                        "low_price": item["low"],
                        "diff": item["change"],
                        "diff_rate": round(item["drate"], 2),
                    }
                )

        df = pd.DataFrame(result)
        df.set_index("code", inplace=True)
        return df

    @with_mock()
    def create_order(
        self,
        asset_code: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = OrderType.MARKET,
        price: int = 0,
        stop_price: int = 0,
        exchange: OrderExchange = OrderExchange.KRX,
    ) -> str:
        """
        주문을 생성합니다.

        Args:
            asset_code (str): 종목 코드
            side (OrderSide): 주문 방향
            quantity (int): 주문 수량
            order_type (OrderType): 주문 유형
            price (int): 주문 가격 (지정가 주문일 경우에만 필요)
            stop_price (int): 스톱 트리거 가격 (스톱 주문일 경우에만 필요)
            exchange (OrderExchange): 거래소

        Returns:
            str: 주문 번호
        """

        def __get_order_type_code():
            if order_type == OrderType.LIMIT:
                return "00"
            elif order_type == OrderType.MARKET:
                return "01"
            elif order_type == OrderType.LIMIT_CONDITIONAL:
                return "02"
            elif order_type == OrderType.BEST_PRICE:
                return "03"
            elif order_type == OrderType.PRIMARY_PRICE:
                return "04"
            elif order_type == OrderType.PRE_MARKET:
                return "05"
            elif order_type == OrderType.AFTER_MARKET:
                return "06"
            elif order_type == OrderType.AFTER_MARKET_SINGLE_PRICE:
                return "07"
            elif order_type == OrderType.LIMIT_IOC:
                return "11"
            elif order_type == OrderType.LIMIT_FOK:
                return "12"
            elif order_type == OrderType.MARKET_IOC:
                return "13"
            elif order_type == OrderType.MARKET_FOK:
                return "14"
            elif order_type == OrderType.BEST_PRICE_IOC:
                return "15"
            elif order_type == OrderType.BEST_PRICE_FOK:
                return "16"
            elif order_type == OrderType.MID_POINT:
                return "21"
            elif order_type == OrderType.MID_POINT_IOC:
                return "23"
            elif order_type == OrderType.MID_POINT_FOK:
                return "24"
            elif order_type == OrderType.STOP_LIMIT:
                return "22"
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        def __get_order_side_code():
            if side == OrderSide.BUY:
                return "buy"
            elif side == OrderSide.SELL:
                return "sell"
            else:
                raise ValueError("지원하지 않는 주문 방향입니다.")

        r = self.stock_api.order_cash(
            self.account_no,
            self.account_product_code,
            __get_order_side_code(),
            asset_code,
            __get_order_type_code(),
            quantity,
            price,
            stop_price,
            self._get_exchange_code(exchange),
        )

        return r["output"]["ODNO"]

    @with_mock()
    def update_order(
        self,
        org_order_no: str,
        order_type: OrderType,
        price: int,
        quantity: int = 0,
        stop_price: int = 0,
        exchange: OrderExchange = OrderExchange.KRX,
    ) -> str:
        """
        주문을 수정합니다.

        Args:
            org_order_no (str): 원주문번호
            order_type (OrderType): 주문 유형
            price (int): 정정 가격
            quantity (int): 주문 수량
            stop_price (int): 스톱 트리거 가격 (스톱 주문일 경우에만 필요)
            exchange (OrderExchange): 거래소

        Returns:
            str: 주문 번호
        """

        def __get_order_type_code():
            if order_type == OrderType.LIMIT:
                return "00"
            elif order_type == OrderType.MARKET:
                return "01"
            elif order_type == OrderType.LIMIT_CONDITIONAL:
                return "02"
            elif order_type == OrderType.BEST_PRICE:
                return "03"
            elif order_type == OrderType.PRIMARY_PRICE:
                return "04"
            elif order_type == OrderType.PRE_MARKET:
                return "05"
            elif order_type == OrderType.AFTER_MARKET:
                return "06"
            elif order_type == OrderType.AFTER_MARKET_SINGLE_PRICE:
                return "07"
            elif order_type == OrderType.LIMIT_IOC:
                return "11"
            elif order_type == OrderType.LIMIT_FOK:
                return "12"
            elif order_type == OrderType.MARKET_IOC:
                return "13"
            elif order_type == OrderType.MARKET_FOK:
                return "14"
            elif order_type == OrderType.BEST_PRICE_IOC:
                return "15"
            elif order_type == OrderType.BEST_PRICE_FOK:
                return "16"
            elif order_type == OrderType.MID_POINT:
                return "21"
            elif order_type == OrderType.MID_POINT_IOC:
                return "23"
            elif order_type == OrderType.MID_POINT_FOK:
                return "24"
            elif order_type == OrderType.STOP_LIMIT:
                return "22"
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        qty_all_ord_yn = "Y" if quantity == 0 else "N"

        r = self.stock_api.order_rvsecncl(
            self.account_no,
            self.account_product_code,
            org_order_no,
            __get_order_type_code(),
            "01",
            quantity,
            price,
            qty_all_ord_yn,
            stop_price,
            self._get_exchange_code(exchange),
        )  # 정정

        return r["output"]["ODNO"]

    @with_mock()
    def cancel_order(
        self,
        org_order_no: str,
        quantity: int = 0,
        stop_price: int = 0,
        exchange: OrderExchange = OrderExchange.KRX,
    ) -> str:
        """
        주문을 취소합니다.

        Args:
            org_order_no (str): 원주문번호
            quantity (int): 취소 수량 (일부 취소의 경우 지정)
            stop_price (int): 스톱 트리거 가격 (스톱 주문일 경우에만 필요)
            exchange (OrderExchange): 거래소
        """
        r = self.stock_api.order_rvsecncl(
            self.account_no,
            self.account_product_code,
            org_order_no,
            "00",
            "02",
            quantity,
            0,
            "Y" if quantity == 0 else "N",
            stop_price,
            excg_id_dvsn_cd=self._get_exchange_code(exchange),
        )  # 취소

        return r["output"]["ODNO"]

    def _get_exchange(self, excg_id_dvsn_cd: str) -> OrderExchange:
        if excg_id_dvsn_cd == "KRX":
            return OrderExchange.KRX
        elif excg_id_dvsn_cd == "NXT":
            return OrderExchange.NXT
        elif excg_id_dvsn_cd == "SOR":
            return OrderExchange.SOR
        else:
            raise ValueError("지원하지 않는 거래소입니다.")

    def _get_exchange_code(self, exchange: OrderExchange) -> str:
        if exchange == OrderExchange.KRX:
            return "KRX"
        elif exchange == OrderExchange.NXT:
            return "NXT"
        elif exchange == OrderExchange.SOR:
            return "SOR"
        else:
            raise ValueError("지원하지 않는 거래소입니다.")

    def get_pending_orders(
        self,
        exchanges: List[OrderExchange] = [OrderExchange.KRX],
    ) -> List[StockOrder]:
        """
        미체결 주문을 조회합니다.

        Args:
            exchanges (List[OrderExchange]): 거래소 리스트

        Returns:
            List[StockOrder]: 미체결 주문 리스트
        """

        fetching = True
        ctx_area_fk100 = ""
        ctx_area_nk100 = ""
        tr_cont = ""

        result: List[StockOrder] = []
        asset_codes = set()

        while fetching:
            r = self.stock_api.inquire_daily_ccld(
                self.account_no,
                self.account_product_code,
                inqr_strt_dt=dtm.date.today(),
                inqr_end_dt=dtm.date.today(),
                ccld_dvsn="02",  # 미체결
                ctx_area_fk100=ctx_area_fk100,
                ctx_area_nk100=ctx_area_nk100,
                tr_cont=tr_cont,
                excg_id_dvsn_cd="ALL",
            )

            output1 = r["output1"]
            for item in output1:
                quantity = int(item["ord_qty"])
                filled_quantity = int(item["tot_ccld_qty"])
                filled_amount = int(item["tot_ccld_amt"])
                pending_quantity = int(item["rmn_qty"])
                filled_price = filled_amount // filled_quantity if filled_quantity > 0 else 0

                order = StockOrder(
                    order_no=item["odno"],
                    asset_code=item["pdno"],
                    side=self._get_order_side_code(item["sll_buy_dvsn_cd"]),
                    quantity=quantity,
                    price=int(item["ord_unpr"]),
                    filled_quantity=filled_quantity,
                    filled_price=filled_price,
                    pending_quantity=pending_quantity,
                    order_time=item["ord_tmd"],
                    current_price=0,
                    is_pending=True,
                    org_order_no=item["orgn_odno"],
                    order_type=self._get_order_type(item["ord_dvsn_cd"]),
                    req_type=self._get_req_type(item["sll_buy_dvsn_cd_name"]),
                    exchange=self._get_exchange(item["excg_id_dvsn_cd"]),
                )

                if order.org_order_no == "0000000000":
                    order.org_order_no = None

                asset_codes.add(item["pdno"])
                result.append(order)

            if r["tr_cont"] in ["F", "M"]:
                ctx_area_fk100 = r["ctx_area_fk100"]
                ctx_area_nk100 = r["ctx_area_nk100"]
                tr_cont = "N"
            else:
                fetching = False

        if len(asset_codes) > 0:
            price_df = self.get_price_for_multiple_stock(list(asset_codes))

        for order in result:
            order.current_price = int(price_df.loc[order.asset_code, "current_price"])

        if not self._is_all_exchanges(exchanges):
            result = [order for order in result if order.exchange in exchanges]

        return result

    def get_pending_orders_old(self) -> List[StockOrder]:
        """
        미체결 주문을 조회합니다.

        Returns:
            List[StockOrder]: 미체결 주문 리스트
        """
        fetching = True
        ctx_area_fk100 = ""
        ctx_area_nk100 = ""

        result: List[StockOrder] = []
        asset_codes = []

        while fetching:
            r = self.stock_api.inquire_psbl_rvsecncl(
                self.account_no,
                self.account_product_code,
                ctx_area_fk100=ctx_area_fk100,
                ctx_area_nk100=ctx_area_nk100,
            )

            for item in r["output"]:
                filled_amount = int(item.get("tot_ccld_amt", 0))
                filled_quantity = int(item.get("tot_ccld_qty", 0))
                filled_price = filled_amount // filled_quantity if filled_quantity > 0 else 0
                asset_code = item["pdno"]

                order = StockOrder(
                    order_no=item["odno"],
                    asset_code=asset_code,
                    side=self._get_order_side_code(item["sll_buy_dvsn_cd"]),
                    price=int(item["ord_unpr"]),
                    filled_price=filled_price,
                    current_price=0,
                    quantity=int(item["ord_qty"]),
                    filled_quantity=filled_quantity,
                    pending_quantity=item["psbl_qty"],
                    order_time=item["ord_tmd"],
                    order_type=self._get_order_type(item["ord_dvsn_cd"]),
                    req_type=self._get_req_type(item["rvse_cncl_dvsn_name"]),
                    exchange=self._get_exchange(item["excg_id_dvsn_cd"]),
                )

                asset_codes.append(asset_code)
                result.append(order)

            if r["tr_cont"] in ["F", "M"]:
                ctx_area_fk100 = r["ctx_area_fk100"]
                ctx_area_nk100 = r["ctx_area_nk100"]
            else:
                fetching = False

        if len(asset_codes) > 0:
            price_df = self.get_price_for_multiple_stock(asset_codes)

        for order in result:
            order.current_price = int(price_df.loc[order.asset_code, "current_price"])

        return result

    def get_today_order_history(
        self,
        target_date: dtm.date = None,
        order_no: str = "",
        exchanges: List[OrderExchange] = [OrderExchange.KRX],
    ) -> List[StockOrder]:
        """
        오늘 주문 내역을 조회합니다.

        Args:
            target_date (dtm.date): 조회할 날짜
            order_no (str): 조회할 주문 번호
            exchange (OrderExchange): 거래소

        Returns:
            List[StockOrder]: 오늘 주문 내역 리스트
        """
        result = []
        fetching = True
        ctx_area_fk100 = ""
        ctx_area_nk100 = ""
        tr_cont = ""

        pending_order_list = [item.order_no for item in self.get_pending_orders()]

        if target_date is None:
            target_date = dtm.date.today()

        while fetching:
            r = self.stock_api.inquire_daily_ccld(
                self.account_no,
                self.account_product_code,
                inqr_strt_dt=target_date,
                inqr_end_dt=target_date,
                odno=order_no,
                ctx_area_fk100=ctx_area_fk100,
                ctx_area_nk100=ctx_area_nk100,
                tr_cont=tr_cont,
                excg_id_dvsn_cd="ALL",
            )

            for item in r["output1"]:
                item["pending"] = item["odno"] in pending_order_list

                quantity = int(item["ord_qty"])
                filled_quantity = int(item["tot_ccld_qty"])
                pending_quantity = quantity - filled_quantity
                filled_price = int(item["avg_prvs"]) if "avg_prvs" in item else 0

                order = StockOrder(
                    order_no=item["odno"],
                    asset_code=item["pdno"],
                    side=self._get_order_side_code(item["sll_buy_dvsn_cd"]),
                    quantity=quantity,
                    price=int(item["ord_unpr"]),
                    filled_quantity=filled_quantity,
                    filled_price=filled_price,
                    pending_quantity=pending_quantity,
                    order_time=item["ord_tmd"],
                    current_price=0,
                    is_pending=item["odno"] in pending_order_list,
                    org_order_no=item["orgn_odno"],
                    order_type=self._get_order_type(item["ord_dvsn_cd"]),
                    req_type=self._get_req_type(item["sll_buy_dvsn_cd_name"]),
                    exchange=self._get_exchange(item["excg_id_dvsn_cd"]),
                )
                result.append(order)

            if r["tr_cont"] in ["F", "M"]:
                ctx_area_fk100 = r["ctx_area_fk100"]
                ctx_area_nk100 = r["ctx_area_nk100"]
                tr_cont = "N"
            else:
                fetching = False

        if not self._is_all_exchanges(exchanges):
            result = [order for order in result if order.exchange in exchanges]

        return result

    def _is_all_exchanges(self, exchanges: List[OrderExchange]) -> bool:
        return set(exchanges) == set(OrderExchange)

    def get_order(self, odno: str) -> StockOrder:
        """
        주문 번호로 주문 정보를 조회합니다.

        당일 주문만 조회 가능합니다.

        Args:
            odno (str): 주문 번호

        Returns:
            StockOrder: 주문 정보
        """
        result = self.get_today_order_history(order_no=odno)
        if len(result) > 0:
            return result[0]
        else:
            return None

    def _get_order_side_code(self, sll_buy_dvsn_cd: str) -> OrderSide:
        if sll_buy_dvsn_cd == "01":
            return OrderSide.SELL
        elif sll_buy_dvsn_cd == "02":
            return OrderSide.BUY
        else:
            raise ValueError("지원하지 않는 주문 방향입니다.")

    def _get_req_type(self, sll_buy_dvsn_cd_name: str) -> OrderRequestType:
        if "취소" in sll_buy_dvsn_cd_name:
            return OrderRequestType.CANCEL
        elif "정정" in sll_buy_dvsn_cd_name:
            return OrderRequestType.MODIFY
        else:
            return OrderRequestType.NEW

    def _get_order_type(self, ord_dvsn_cd: str) -> OrderType:
        if ord_dvsn_cd == "00":
            return OrderType.LIMIT
        elif ord_dvsn_cd == "01":
            return OrderType.MARKET
        elif ord_dvsn_cd == "02":
            return OrderType.LIMIT_CONDITIONAL
        elif ord_dvsn_cd == "03":
            return OrderType.BEST_PRICE
        elif ord_dvsn_cd == "04":
            return OrderType.PRIMARY_PRICE
        elif ord_dvsn_cd == "05":
            return OrderType.PRE_MARKET
        elif ord_dvsn_cd == "06":
            return OrderType.AFTER_MARKET
        elif ord_dvsn_cd == "07":
            return OrderType.AFTER_MARKET_SINGLE_PRICE
        elif ord_dvsn_cd == "08":
            return OrderType.SELF_STOCK
        elif ord_dvsn_cd == "09":
            return OrderType.SELF_STOCK_S_OPTION
        elif ord_dvsn_cd == "10":
            return OrderType.SELF_STOCK_MONETARY_TRUST
        elif ord_dvsn_cd == "11":
            return OrderType.LIMIT_IOC
        elif ord_dvsn_cd == "12":
            return OrderType.LIMIT_FOK
        elif ord_dvsn_cd == "13":
            return OrderType.MARKET_IOC
        elif ord_dvsn_cd == "14":
            return OrderType.MARKET_FOK
        elif ord_dvsn_cd == "15":
            return OrderType.BEST_PRICE_IOC
        elif ord_dvsn_cd == "16":
            return OrderType.BEST_PRICE_FOK
        elif ord_dvsn_cd == "21":
            return OrderType.MID_POINT
        elif ord_dvsn_cd == "22":
            return OrderType.STOP_LIMIT
        elif ord_dvsn_cd == "23":
            return OrderType.MID_POINT_IOC
        elif ord_dvsn_cd == "24":
            return OrderType.MID_POINT_FOK
        else:
            raise ValueError(f"지원하지 않는 주문 유형입니다. {ord_dvsn_cd}")

    async def listen_order_event(self, stop_event: Optional[asyncio.Event] = None) -> AsyncGenerator:
        """
        계좌 주문 이벤트를 수신하는 메서드

        Args:
            stop_event (asyncio.Event): 종료 이벤트

        Yields:
            OrderEvent: 주문 이벤트
        """
        assert self.hts_id is not None, "HTS ID가 필요합니다."

        async for data in self.stock_api.listen_order_event(self.hts_id, stop_event):
            order_event = self.map_order_event(data)
            yield order_event

    def map_order_event(self, data: dict) -> OrderEvent:
        def __find_order_type(value):
            value_map = {
                "00": OrderType.LIMIT,
                "01": OrderType.MARKET,
                "02": OrderType.LIMIT_CONDITIONAL,
                "03": OrderType.BEST_PRICE,
                "04": OrderType.PRIMARY_PRICE,
                "11": OrderType.LIMIT_IOC,
                "12": OrderType.LIMIT_FOK,
                "13": OrderType.MARKET_IOC,
                "14": OrderType.MARKET_FOK,
                "15": OrderType.BEST_PRICE_IOC,
                "16": OrderType.BEST_PRICE_FOK,
            }
            # 장전후 시간외 및 단일거 거래는 시장가로 반환
            return value_map.get(value, OrderType.MARKET)

        acpt_yn = data.get("acpt_yn")  # 1:주문접수 2:확인 3:취소(FOK/IOC)
        cntg_yn = data.get("cntg_yn")  # 1:주문,정정,취소,거부 2:체결

        account_no = data["acnt_no"]
        asset_code = data["stck_shrn_iscd"]
        order_no = data["oder_no"]
        side = OrderSide.SELL if data["seln_byov_cls"] == "01" else OrderSide.BUY
        order_type = None
        quantity = 0
        price = None
        event_type = ""
        filled_quantity = 0
        filled_price = None
        filled_time = data["stck_cntg_hour"]
        org_order_no = data["ooder_no"]

        rejected = data.get("rfus_yn") == "1"
        rctf_cls = data.get("rctf_cls")  # 0: 신규, 1: 정정, 2: 취소

        cancelled = rctf_cls == "2" and (acpt_yn == "2" or acpt_yn == "3") and cntg_yn == "1"
        updated = rctf_cls == "1" and acpt_yn == "2" and cntg_yn == "1"
        accepted = rctf_cls == "0" and acpt_yn == "1" and cntg_yn == "1"
        executed = cntg_yn == "2"

        if cntg_yn == "1":  # 주문,정정,취소,거부
            price = data["cntg_unpr"]
            quantity = data["cntg_qty"]
            order_type = __find_order_type(data["oder_kind"])
        elif cntg_yn == "2":  # 체결
            price = int(data["oder_prc"])
            quantity = data["oder_qty"]
            filled_price = data["cntg_unpr"]
            filled_quantity = data["cntg_qty"]

        if rejected:
            event_type = "rejected"
        elif cancelled:
            event_type = "cancelled"
            # IOC 취소될땐 org_order_no가 비어있어서 오류 발생함
            if org_order_no:
                order_no = org_order_no  # 취소 주문의 경우 원주문번호로 변경
                org_order_no = None
        elif accepted or updated:
            event_type = "accepted"
        elif executed:
            event_type = "executed"

        if filled_time is not None:
            t = dtm.datetime.strptime(filled_time, "%H%M%S").time()
            filled_time = dtm.datetime.combine(dtm.date.today(), t)

        ord_exg_gb = data.get("ord_exg_gb")
        exchange = None
        if ord_exg_gb == "1":
            exchange = OrderExchange.KRX
        elif ord_exg_gb == "2":
            exchange = OrderExchange.NXT
        elif ord_exg_gb == "3":
            exchange = OrderExchange.SOR
        elif ord_exg_gb == "4":
            exchange = OrderExchange.SOR

        if account_no == f"{self.account_no}{self.account_product_code}":
            print(f"- rctf_cls={rctf_cls} acpt_yn={acpt_yn} cntg_yn={cntg_yn} accepted={accepted} executed={executed} rejected={rejected} status={event_type}")

        return OrderEvent(
            asset_code,
            order_no,
            side,
            order_type,
            quantity,
            price,
            event_type,
            account_no,
            filled_quantity,
            filled_price,
            filled_time,
            org_order_no,
            exchange=exchange,
        )

    def get_orderbook(self, asset_code: str, data_exchange: DataExchange = DataExchange.KRX) -> Dict:
        """
        특정 종목의 호가/잔량 정보를 조회하여 반환합니다.

        Args:
            asset_code (str): 조회할 자산의 종목번호.
            data_exchange(DataExchange): 데이터 거래소

        Returns:
            dict: 호가 정보가 포함된 사전.
                - total_bid_volume (int): 총 매수 잔량.
                - total_ask_volume (int): 총 매도 잔량.
                - ask_price (int): 1차 매도 호가 가격.
                - ask_volume (int): 1차 매도 호가 잔량.
                - bid_price (int): 1차 매수 호가 가격.
                - bid_volume (int): 1차 매수 호가 잔량.
                - time (dtm.datetime): 현지 기준 호가 정보 조회 시간.
                - bids (list): 매수 호가 목록 (각 항목은 price와 volume을 포함하는 dict).
                - asks (list): 매도 호가 목록 (각 항목은 price과 volume을 포함하는 dict).

        Raises:
            ValueError: 주어진 티커가 유효하지 않거나 찾을 수 없는 경우 발생.
        """

        r = self.stock_api.inquire_asking_price_exp_ccn(asset_code, self._get_data_exchange(data_exchange))

        o1 = r["output1"]
        if not o1:
            return {}

        result = {
            "total_bid_volume": o1["total_bidp_rsqn"],
            "total_ask_volume": o1["total_askp_rsqn"],
            "ask_price": o1["askp1"],
            "ask_volume": o1["askp_rsqn1"],
            "bid_price": o1["bidp1"],
            "bid_volume": o1["bidp_rsqn1"],
            "time": dtm.datetime.combine(dtm.date.today(), o1["aspr_acpt_hour"]),
            "bids": [{"price": o1[f"bidp{i}"], "volume": o1[f"bidp_rsqn{i}"]} for i in range(1, 11)],
            "asks": [{"price": o1[f"askp{i}"], "volume": o1[f"askp_rsqn{i}"]} for i in range(1, 11)],
        }

        return result
