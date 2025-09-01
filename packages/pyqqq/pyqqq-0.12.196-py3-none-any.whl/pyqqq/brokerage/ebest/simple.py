from dataclasses import dataclass
from decimal import Decimal
from pyqqq.brokerage.ebest.domestic_stock import EBestDomesticStock
from pyqqq.brokerage.ebest.oauth import EBestAuth
from pyqqq.data.realtime import get_all_last_trades
from pyqqq.datatypes import *
from pyqqq.utils.logger import get_logger
from pyqqq.utils.mock_api import with_mock
from typing import AsyncGenerator, List, Set
import asyncio
import datetime as dtm
import pandas as pd
import time


@dataclass
class EBestStockPosition(StockPosition):
    pass


@dataclass
class EBestStockOrder(StockOrder):
    pass


class EBestSimpleDomesticStock:
    """
    LS(구 이베스트투자)증권 국내 주식 API 사용하여 주식 거래를 하기 위한 클래스입니다.

    기존 EBestDomesticStock 클래스를 감싸고, 간단한 주문/조회 기능을 제공합니다.

    Attributes:
        auth (EBestAuth): 인증 정보
    """

    def __init__(self, auth: EBestAuth):
        self.stock_api = EBestDomesticStock(auth)
        self.logger = get_logger(__name__ + ".EBestSimpleDomesticStock")

    @with_mock()
    def get_account(self) -> dict:
        """
        계좌 정보를 조회합니다.

        Returns:
            dict: 계좌 정보

            - account_no (str): 계좌 번호
            - total_balance (int): 총 평가 금액
            - purchase_amount (int): 매입 금액
            - evaluated_amount (int): 평가 금액
            - pnl_amount (int): 손익 금액
            - pnl_rate (Decimal): 손익률
        """

        r = self.stock_api.get_stock_balance()

        data = r["output1"]

        purchase_amount = data["mamt"]
        evaluated_amount = data["tappamt"]
        pnl_amount = data["tdtsunik"]
        pnl_rate = Decimal(pnl_amount / purchase_amount * 100) if purchase_amount != 0 else Decimal(0)

        result = {
            "total_balance": data["sunamt"],
            "purchase_amount": purchase_amount,
            "evaluated_amount": evaluated_amount,
            "pnl_amount": pnl_amount,
            "pnl_rate": pnl_rate,
        }

        r = self.stock_api.get_account_deposit_orderable_total_evaluation()
        result["account_no"] = r["output1"]["AcntNo"]
        result["investable_cash"] = r["output2"]["MnyOrdAbleAmt"]

        return result

    @with_mock()
    def get_possible_quantity(self, asset_code: str, order_type: OrderType = OrderType.MARKET, price: int = 0) -> dict:
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
        resp = self.stock_api.get_account_orderable_quantity(
            2,
            asset_code,
            price,
        )

        output1 = resp["output1"]
        output2 = resp["output2"]
        result = {
            "investable_cash": output2["MnyOrdAbleAmt"],
            "reusable_amount": output2["RuseObjAmt"],
            "price": int(Decimal(output1["OrdPrc"])),
            "quantity": output2["OrdAbleQty"],
            "amount": output2["OrdAbleAmt"],
        }
        return result

    @with_mock()
    def get_positions(self) -> List[StockPosition]:
        """
        보유 종목을 조회합니다.

        Returns:
            List[StockPosition]: 보유 종목 정보 리스트
        """

        tr_cont_key = ""
        cts_expcode = ""

        fetching = True
        result = []

        while fetching:
            r = self.stock_api.get_stock_balance(tr_cont_key=tr_cont_key, cts_expcode=cts_expcode)

            output1 = r["output1"]
            output2 = r["output2"]

            tr_cont_key = output1.get("tr_cont_key", "")
            cts_expcode = output1.get("cts_expcode", "")

            for el in output2:
                position = StockPosition(
                    asset_code=el["expcode"],
                    asset_name=el["hname"],
                    quantity=int(el["janqty"]),
                    sell_possible_quantity=int(el["mdposqt"]),
                    average_purchase_price=Decimal(el["pamt"]),
                    current_price=int(el["price"]),
                    current_value=int(el["appamt"]),
                    current_pnl=Decimal(el["sunikrt"]),
                    current_pnl_value=int(el["dtsunik"]),
                )

                if position.quantity > 0:
                    result.append(position)

            if cts_expcode.strip() == "":
                fetching = False

        return result

    @with_mock()
    def get_historical_daily_data(
        self,
        asset_code: str,
        first_date: dtm.date,
        last_date: dtm.date,
        adjusted_price: bool = True,
    ) -> pd.DataFrame:
        """
        일봉 데이터 검색

        Args:
            asset_code(str): 종목코드
            first_date(datetime.date): 조회 시작일자
            last_date(datetime.date): 조회 종료일자
            adjusted_price(bool): 수정 주가 여부

        Returns:
            pd.DataFrame: 일봉 데이터
        """
        assert first_date <= last_date, "last_date는 first_date와 같거나, 이후 날짜여야 합니다"
        assert last_date <= dtm.date.today(), "last_date는 오늘과 같거나 이전이어야 합니다."

        cts_date = ""
        tr_cont_key = ""

        fetching = True
        result = []

        while fetching:
            r = self.stock_api.get_stock_chart_dwmy(
                asset_code,
                "d",
                last_date,
                first_date,
                cts_date=cts_date,
                tr_cont_key=tr_cont_key,
                sujung_yn=adjusted_price,
            )

            output1 = r["output1"]

            tr_cont_key = r.get("tr_cont_key", "")
            cts_date = output1.get("cts_date", "").strip()

            output2 = r["output2"]
            output2.reverse()

            for item in output2:
                if not item:
                    continue

                result.append(
                    {
                        "date": dtm.datetime.strptime(item["date"], "%Y%m%d").date(),
                        "open": item["open"],
                        "high": item["high"],
                        "low": item["low"],
                        "close": item["close"],
                        "volume": item["jdiff_vol"],
                    }
                )

            if r["tr_cont"] == "N" or cts_date == "":
                fetching = False

        df = pd.DataFrame(result)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        return df

    def get_today_minute_data(self, asset_code: str) -> pd.DataFrame:
        """
        분봉 데이터 검색

        Args:
            asset_code(str): 종목코드

        Returns:
            pd.DataFrame: 분봉 데이터
        """

        fetching = True
        tr_cont_key = ""
        cts_date = ""
        cts_time = ""
        result = []

        while fetching:
            r = self.stock_api.get_stock_chart_minutes(
                asset_code,
                1,
                500,
                0,
                dtm.date.today(),
                dtm.date.today(),
                cts_date,
                cts_time,
                tr_cont_key=tr_cont_key,
            )

            tr_cont = r["tr_cont"]
            tr_cont_key = r["tr_cont_key"]

            output1 = r["output1"]
            cts_date = output1.get("cts_date", "")
            cts_time = output1.get("cts_time", "")

            output2 = r["output2"]
            output2.reverse()

            for item in output2:
                if not item:
                    continue

                datetime = dtm.datetime.strptime(f"{item['date']} {item['time']}", "%Y%m%d %H%M%S")

                result.append(
                    {
                        "time": datetime,
                        "open": item["open"],
                        "high": item["high"],
                        "low": item["low"],
                        "close": item["close"],
                        "volume": item["jdiff_vol"],
                    }
                )

            if tr_cont == "N" or (cts_date == "" and cts_time == ""):
                fetching = False

        df = pd.DataFrame(result)
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
        df.set_index("time", inplace=True)

        return df

    def get_price(self, asset_code: str) -> dict:
        """
        주식 현재 가격 조회

        Args:
            asset_code(str): 종목코드

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
            - diff (int): 전일 대비 가격 변화
            - diff_rate (float): 전일 대비 가격 변화율
        """
        r = self.stock_api.get_price(asset_code)

        data = r["output"]
        result = {
            "code": asset_code,
            "current_price": data["price"],
            "volume": data["volume"],
            "open_price": data["open"],
            "high_price": data["high"],
            "low_price": data["low"],
            "max_price": data["uplmtprice"],
            "min_price": data["dnlmtprice"],
            "diff": data["change"],
            "diff_rate": float(data["diff"]),
        }

        return result

    def get_price_for_multiple_stock(self, asset_codes: Set[str]) -> pd.DataFrame:
        """
        여러 종목의 현재 가격 조회

        Args:
            asset_codes(Set[str]): 종목 코드 리스트

        Returns:
            pd.DataFrame: 현재 가격 정보

            - code (str): 종목 코드
            - current_price (int): 현재 가격
            - volume (int): 거래량
            - open_price (int): 시가
            - high_price (int): 고가
            - low_price (int): 저가
            - diff (int): 전일 대비 가격 변화
            - diff_rate (float): 전일 대비 가격 변화율
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
    ) -> str:
        """
        주문을 생성합니다.

        Args:
            asset_code (str): 종목 코드
            side (OrderSide): 주문 방향
            quantity (int): 주문 수량
            order_type (OrderType): 주문 유형
            price (int): 주문 가격 (지정가 주문일 경우에만 필요)

        Returns:
            str: 주문 번호
        """

        def __get_ord_prc_ptn_code():
            if order_type == OrderType.MARKET:
                return "03"
            elif order_type == OrderType.LIMIT:
                return "00"
            elif order_type == OrderType.LIMIT_IOC:
                return "00"
            elif order_type == OrderType.LIMIT_FOK:
                return "00"
            elif order_type == OrderType.MARKET_IOC:
                return "03"
            elif order_type == OrderType.MARKET_FOK:
                return "03"
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        def __get_ord_cndi_tp_code() -> int:
            if order_type in [OrderType.MARKET, OrderType.LIMIT]:
                return 0
            elif order_type in [OrderType.MARKET_IOC, OrderType.LIMIT_IOC]:
                return 1
            elif order_type in [OrderType.MARKET_FOK, OrderType.LIMIT_FOK]:
                return 2
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        def __get_bns_tp_code() -> int:
            if side == OrderSide.BUY:
                return 2
            elif side == OrderSide.SELL:
                return 1
            else:
                raise ValueError("지원하지 않는 주문 방향입니다.")

        r = self.stock_api.create_order(
            asset_code,
            quantity,
            price,
            __get_bns_tp_code(),
            __get_ord_prc_ptn_code(),
            ord_cndi_tp_code=__get_ord_cndi_tp_code(),
        )

        self.logger.info(f"create_order result - {r['rsp_cd']} {r['rsp_msg']}")

        if "OrdNo" not in r["output2"]:
            self.logger.error(f"create_order failed. {asset_code} {side} {quantity} {order_type} {price} - {r['rsp_cd']} {r['rsp_msg']}")

        return r["output2"].get("OrdNo", None)

    @with_mock()
    def update_order(
        self,
        org_order_no: str,
        asset_code: str,
        order_type: OrderType,
        price: int,
        quantity: int = 0,
    ) -> str:
        """
        주문을 수정합니다.

        Args:
            org_order_no (str): 원주문번호
            order_type (OrderType): 주문 유형
            price (int): 정정 가격
            quantity (int): 주문 수량

        Returns:
            str: 주문 번호
        """

        def __get_ord_prc_ptn_code():
            if order_type == OrderType.MARKET:
                return "03"
            elif order_type == OrderType.LIMIT:
                return "00"
            elif order_type == OrderType.LIMIT_IOC:
                return "00"
            elif order_type == OrderType.LIMIT_FOK:
                return "00"
            elif order_type == OrderType.MARKET_IOC:
                return "03"
            elif order_type == OrderType.MARKET_FOK:
                return "03"
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        def __get_ord_cndi_tp_code() -> int:
            if order_type in [OrderType.MARKET, OrderType.LIMIT]:
                return 0
            elif order_type in [OrderType.MARKET_IOC, OrderType.LIMIT_IOC]:
                return 1
            elif order_type in [OrderType.MARKET_FOK, OrderType.LIMIT_FOK]:
                return 2
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        r = self.stock_api.update_order(
            org_order_no,
            asset_code,
            quantity,
            __get_ord_prc_ptn_code(),
            __get_ord_cndi_tp_code(),
            price,
        )

        return r["output2"]["OrdNo"]

    @with_mock()
    def cancel_order(self, org_order_no: str, asset_code: str, quantity: int) -> str:
        """
        주문을 취소합니다.

        Args:
            org_order_no (str): 원주문번호
            quantity (int): 취소 수량
        """

        r = self.stock_api.cancel_order(org_order_no, asset_code, quantity)

        return r["output2"]["OrdNo"]

    def get_pending_orders(self) -> List[StockOrder]:
        """
        미체결 주문을 조회합니다.

        Returns:
            List[StockOrder]: 미체결 주문 리스트
        """

        fetching = True
        tr_cont_key = ""
        cts_ordno = ""

        result: List[StockOrder] = []
        asset_codes = set()

        def __find_req_type(medosu: str) -> OrderRequestType:
            if "취소" in medosu:
                return OrderRequestType.CANCEL
            elif "정정" in medosu:
                return OrderRequestType.MODIFY
            else:
                return OrderRequestType.NEW

        while fetching:
            r = self.stock_api.get_order_list(
                chegb="2",
                cts_ordno=cts_ordno,
                tr_cont_key=tr_cont_key,
            )

            output1 = r["output1"]
            output2 = r["output2"]

            tr_cont_key = r["tr_cont_key"]
            cts_ordno = output1.get("cts_ordno", "")

            for item in output2:
                asset_code = item["expcode"]
                ord_time = dtm.datetime.strptime(item["ordtime"], "%H%M%S%f")

                order = StockOrder(
                    order_no=str(item["ordno"]),
                    asset_code=asset_code,
                    side=OrderSide.SELL if "매도" in item["medosu"] else OrderSide.BUY,
                    price=int(item["price"]),
                    filled_price=item["cheprice"],
                    current_price=0,
                    quantity=int(item["qty"]),
                    filled_quantity=item["cheqty"],
                    pending_quantity=item["ordrem"],
                    order_time=dtm.datetime.combine(dtm.date.today(), ord_time.time()),
                    org_order_no=item.get("orgordno", None),
                    is_pending=True,
                    req_type=__find_req_type(item["medosu"]),
                )

                asset_codes.add(asset_code)
                result.append(order)

            if cts_ordno == "":
                fetching = False

        if len(asset_codes) > 0:
            price_df = self.get_price_for_multiple_stock(asset_codes)

        for order in result:
            order.current_price = int(price_df.loc[order.asset_code, "current_price"])

        return result

    def get_today_order_history(self) -> List[StockOrder]:
        """
        오늘 주문 내역을 조회합니다.

        Returns:
            List[StockOrder]: 오늘 주문 내역 리스트
        """
        fetching = True
        tr_cont_key = ""
        cts_ordno = ""

        result: List[StockOrder] = []
        asset_codes = set()

        detail_info_dict = self._get_today_order_details()

        while fetching:
            r = self.stock_api.get_order_list(
                cts_ordno=cts_ordno,
                tr_cont_key=tr_cont_key,
            )

            output1 = r["output1"]
            output2 = r["output2"]

            tr_cont_key = r["tr_cont_key"]
            cts_ordno = output1.get("cts_ordno", "")

            for item in output2:
                asset_code = item["expcode"]
                ord_time = dtm.datetime.strptime(item["ordtime"], "%H%M%S%f")
                order_no = str(item["ordno"])
                order = StockOrder(
                    order_no=order_no,
                    asset_code=asset_code,
                    side=detail_info_dict[order_no]["side"],
                    price=int(item["price"]),
                    filled_price=item["cheprice"],
                    current_price=0,
                    quantity=int(item["qty"]),
                    filled_quantity=item["cheqty"],
                    pending_quantity=item["ordrem"],
                    order_time=dtm.datetime.combine(dtm.date.today(), ord_time.time()),
                    org_order_no=item.get("orgordno", None),
                    is_pending=(not item["status"] in ["완료", "체결", "취소확인"]),
                    req_type=detail_info_dict[order_no]["req_type"],
                    order_type=detail_info_dict[order_no]["order_type"],
                )

                asset_codes.add(asset_code)
                result.append(order)

            if cts_ordno == "":
                fetching = False

        if len(asset_codes) > 0:
            price_df = self.get_price_for_multiple_stock(asset_codes)

        for order in result:
            order.current_price = int(price_df.loc[order.asset_code, "current_price"])

        return result

    def _get_today_order_details(self) -> dict:
        r = self.stock_api.get_deposit_order_list()

        result = {}

        def __find_req_type(mrc_tp_code: str) -> OrderRequestType:
            if mrc_tp_code == "2":
                return OrderRequestType.CANCEL
            elif mrc_tp_code == "1":
                return OrderRequestType.MODIFY
            else:
                return OrderRequestType.NEW

        def __find_side(bns_tp_code: str) -> OrderSide:
            if bns_tp_code == "2":
                return OrderSide.BUY
            elif bns_tp_code == "1":
                return OrderSide.SELL
            else:
                raise ValueError("지원하지 않는 주문 방향입니다.")

        def __find_order_type(ord_prc_ptn_code: str, ord_cndi_tp_code: str) -> OrderType:
            if ord_prc_ptn_code == "00":
                if ord_cndi_tp_code == "0":
                    return OrderType.LIMIT
                elif ord_cndi_tp_code == "1":
                    return OrderType.LIMIT_IOC
                elif ord_cndi_tp_code == "2":
                    return OrderType.LIMIT_FOK
            elif ord_prc_ptn_code == "03":
                if ord_cndi_tp_code == "0":
                    return OrderType.MARKET
                elif ord_cndi_tp_code == "1":
                    return OrderType.MARKET_IOC
                elif ord_cndi_tp_code == "2":
                    return OrderType.MARKET_FOK
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        for item in r["output3"]:
            order_no = str(item["OrdNo"])
            result[order_no] = {
                "side": __find_side(item["BnsTpCode"]),
                "req_type": __find_req_type(item["MrcTpCode"]),
                "order_type": __find_order_type(item["OrdprcPtnCode"], item["OrdCndiTpCode"]),
            }

        return result

    def get_tick_data(self, asset_code) -> list:
        fetching = True
        tr_cont_key = ""
        tr_cont = ""
        cts_time = ""
        result = []

        while fetching:
            r = self.stock_api.get_stock_tick_data_today_yesterday(
                daygb=0,
                timegb=1,
                shcode=asset_code,
                endtime=dtm.datetime.now().time(),
                cts_time=cts_time,
                tr_cont_key=tr_cont_key,
            )

            output1 = r["output1"]
            output2 = r["output2"]

            cts_time = output1.get("cts_time", "")
            tr_cont_key = output1.get("tr_cont_key", "")

            for item in output2:
                result.append(item)

            if tr_cont == "N" or cts_time == "":
                fetching = False

            else:
                tr_cont = "Y"
                self.logger.debug(f"get_tick_data: sleep 1 for next page request. current length: {len(result)} cts_time={cts_time} tr_cont_key={tr_cont_key}")
                time.sleep(1)

        return result

    async def listen_order_event(self, stop_event: asyncio.Event) -> AsyncGenerator:
        """
        계좌 주문 이벤트를 수신하는 메서드

        Args:
            stop_event (asyncio.Event): 종료 이벤트

        Yields:
            OrderEvent: 주문 이벤트
        """
        async for data in self.stock_api.listen_order_event(stop_event):
            order_event = self._map_order_event(data)
            if order_event is not None:
                yield order_event

    def _map_order_event(self, data: dict) -> OrderEvent:
        if data.get("ordchegb") == "03" and data["event_type"] == "accepted":
            # 주문 취소 요청에 대한 접수 이벤트는 무시
            return

        if data.get("ordchegb") == "02" and data["event_type"] == "accepted":
            # 주문 정정 요청에 대한 접수 이벤트는 무시
            return

        def __find_order_type(data: dict) -> str:
            value_map = {
                "00": OrderType.LIMIT,
                "03": OrderType.MARKET,
                "05": OrderType.LIMIT_CONDITIONAL,
                "06": OrderType.BEST_PRICE,
                "07": OrderType.PRIMARY_PRICE,
                "13": OrderType.MARKET_IOC,
                "16": OrderType.BEST_PRICE_IOC,
                "26": OrderType.BEST_PRICE_FOK,
            }

            if "ordprcptncode" in data:
                code = data["ordprcptncode"]
                return value_map.get(code, code)
            elif "etfhogagb" in data:
                code = data["etfhogagb"]
                return value_map.get(code, code)

        def __find_status(data: dict) -> str:
            event_type = data["event_type"]
            if event_type == "accepted" or event_type == "updated":
                return "accepted"
            elif event_type == "executed":
                return "executed"
            elif event_type == "cancelled":
                return "cancelled"
            elif event_type == "denied":
                return "rejected"
            else:
                return event_type

        asset_code = ""
        if "shtcode" in data:
            asset_code = data["shtcode"]
        elif "shtnIsuno" in data:
            asset_code = data["shtnIsuno"]

        if asset_code[0] in ["A", "J"]:
            asset_code = asset_code[1:]

        account_no = data["accno"]

        # 취소 주문의 경우 원주문번호를 사용
        order_no = str(data["orgordno"] if data["event_type"] == "cancelled" else data["ordno"])
        side = OrderSide.BUY if data["bnstp"] == "2" else OrderSide.SELL
        order_type = __find_order_type(data)
        quantity = int(data["ordqty"])
        price = int(data["ordprice"]) if "ordprice" in data else int(data["ordprc"])
        event_type = __find_status(data)

        filled_quantity = int(data["execqty"]) if data.get("execqty", "").strip() != "" else None
        filled_price = int(data["execprc"]) if data.get("execprc", "").strip() != "" else None
        pending_quantity = int(data["unercqty"]) if data.get("unercqty", "").strip() != "" else None

        filled_time = data.get("rcptexectime")
        org_order_no = str(data.get("orgordno")) if data["event_type"] != "cancelled" else None

        self.logger.debug(f"order_event: order_no={order_no} / filled={filled_quantity} order={quantity} pending={pending_quantity} event_type={event_type}")

        if filled_time is not None:
            t = dtm.datetime.strptime(filled_time, "%H%M%S%f").time()
            filled_time = dtm.datetime.combine(dtm.date.today(), t)

        order_event = OrderEvent(
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
        )

        return order_event
