from dataclasses import asdict
from decimal import ROUND_HALF_UP, Decimal
from pyqqq.brokerage.ebest.simple import EBestSimpleDomesticStock
from pyqqq.brokerage.kis.simple import KISSimpleDomesticStock
from pyqqq.data.domestic import get_tickers
from pyqqq.datatypes import *
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.array import find
from pyqqq.utils.logger import get_logger
from pyqqq.utils.market_schedule import get_market_schedule, get_last_trading_day
from pyqqq.utils.singleton import singleton
from typing import Dict, Optional, List
import asyncio
import os
import pyqqq.config as c
import datetime as dtm


@singleton
class TrackerSocket:
    """
    거래 내역 추적을 위한 WebSocket 소켓 클래스입니다.

    Args:
        simple_api (EBestSimpleDomesticStock | KISSimpleDomesticStock): 간편 거래 API 객체
    """

    def __init__(self, simple_api: EBestSimpleDomesticStock | KISSimpleDomesticStock):
        self.simple_api = simple_api
        self.task: asyncio.Task = None
        self.stop_event = asyncio.Event()
        self.logger = get_logger(__name__ + ".TrackerSocket")
        self.trading_tracker_counter = 1
        self.only_my_account = True
        self.event_callbacks: Dict[callable] = {}

    async def start(self):
        """
        TradingSocket에서 거래내역 추적을 시작합니다.
        """
        if self.task is not None and not self.task.done():
            self.logger.info("TrackerSocket already started!")
            return

        self.task = asyncio.create_task(self._listen_order_event())
        self.logger.info("TrackerSocket started!")

    async def _listen_order_event(self):
        """
        주문 이벤트를 수신하고 처리하는 비동기 메서드입니다.
        """
        self.logger.info("Listening for order events...")
        try:
            async for event in self.simple_api.listen_order_event(self.stop_event):
                self._relay_order_event(event)
        except asyncio.CancelledError:
            self.logger.info("Order event listening cancelled.")
        except Exception as e:
            self.logger.exception(f"Error while listening to order events: {e}")

    def _relay_order_event(self, event: OrderEvent):
        """
        주문 이벤트를 등록된 콜백 함수로 전달합니다.

        Args:
            event (OrderEvent): 주문 이벤트 객체
        """
        if event is None or (self.only_my_account and not self._check_account_match(event.account_no)):
            return

        self.logger.debug(f"Relay order event: {event}")

        for callback in self.event_callbacks.values():
            try:
                callback(event)
            except Exception as e:
                self.logger.exception(f"Error in callback {callback}: {e}")

    def add_tracker(self, callback: callable):
        """
        TradingTracker를 추가합니다.

        Args:
            callback (callable): 거래 내역 추적 이벤트를 처리할 콜백 함수
        """
        ret = self.trading_tracker_counter
        self.event_callbacks[self.trading_tracker_counter] = callback
        self.trading_tracker_counter += 1

        self.logger.info(f"Tracker added: {ret}")
        return ret

    async def remove_tracker(self, tracker_number: int):
        """
        TradingTracker를 제거합니다.
        Args:
            tracker_number (int): 제거할 트래커 번호
        """
        if tracker_number in self.event_callbacks:
            del self.event_callbacks[tracker_number]
            self.logger.info(f"Tracker removed: {tracker_number}")
        else:
            self.logger.warning(f"Tracker {tracker_number} not found!")

        if len(self.event_callbacks) == 0:
            self.logger.info("No more trackers, stopping TrackerSocket.")
            await self.stop()

    async def stop(self):
        """
        거래 내역 추적을 중지합니다.
        """
        if self.task is None or self.task.done():
            self.logger.info("TrackerSocket already stopped!")
            return

        self.stop_event.set()
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass
        self.logger.info("TrackerSocket stopped!")

        self.task = asyncio.create_task(self._monitor_schedule())

    def _check_account_match(self, event_account_no):
        my_account_no = f"{self.simple_api.account_no}{self.simple_api.account_product_code}"

        if event_account_no is not None and my_account_no == event_account_no:
            return True
        else:
            return False

    def activate_all_account_event(self):
        """
        내 hts_id에 연동된 모든 계좌의 주문을 수신하도록 설정합니다.
        """
        self.only_my_account = False


class TradingTracker:
    """
    거래 내역 추적을 위한 클래스입니다

    주문 이벤트를 수신하여 보유 포지션과 미체결 주문을 관리하고 거래 내역을 기록합니다.

    Args:
        simple_api (EBestSimpleDomesticStock | KISSimpleDomesticStock): 간편 거래 API 객체
        fee_rate (Decimal): 증권사 수수료율 (기본값: 0.015%)
    """

    logger = get_logger(__name__ + ".TradingTracker")

    def __init__(
        self,
        simple_api: EBestSimpleDomesticStock | KISSimpleDomesticStock,
        fee_rate: Decimal = Decimal("0.00015"),  # 뱅키스, LS증권 수수료율 0.015%
    ):
        self.positions: List[StockPosition] = []
        """ 보유 포지션 목록 """

        self.pending_orders: List[StockOrder] = []
        """ 미체결 주문 목록 """

        self.on_pending_order_update: Optional[callable] = None
        """ (deprecated) 미체결 주문 업데이트 이벤트 callback """

        self.on_position_update: Optional[callable] = None
        """ (deprecated) 포지션 업데이트 callback """

        self.on_pending_order_update_callback_dict: Dict[callable] = {}
        """ 미체결 주문 업데이트 이벤트 callback dict
        key: callback_id
        value: callback[callable]

        Args:
            status (str): 이벤트 상태. 'accepted', 'cancelled', 'completed', 'partial'
            order (StockOrder): 주문 정보
        """

        self.on_position_update_callback_dict: Dict[callable] = {}
        """ 포지션 업데이트 이벤트 callback dict
        key: callback_id
        value: callback[callable]

        Args:
            type (str): 이벤트 타입. 'added', 'modified', 'removed'
            position (StockPosition): 포지션 정보
        """

        self.task: asyncio.Task = None
        """ 백그라운드로 실행되는 거래 이벤트 모니터링 Task """

        self.simple_api = simple_api
        self.account_no = None
        self.fee_rate = fee_rate  # 증권사 수수료율
        self.tax_rate = Decimal("0.0018")  # KOSPI, KOSDAQ 매도시 거래세율 0.18%
        self.tickers: Dict[str, Dict] = {}  # 종목 코드별 종목 정보
        self.ticker_date: dtm.datetime = None  # 종목 정보 갱신 시간
        self.save_trading_history = False  # 거래 내역 저장 여부
        self.last_t_day_tickers: Dict[str, Dict] = {}
        self.tracker_socket = TrackerSocket(simple_api)
        self.tracker_number = None

        self.started = False
        self.callback_id = 0

    async def start(self):
        """
        거래 내역 추적을 시작합니다
        """
        if self.started:
            self.logger.info(f"Trading tracker already started!")
            return
        if isinstance(self.simple_api, EBestSimpleDomesticStock):
            account_info = self.simple_api.get_account()
            self.account_no = account_info["account_no"]
        elif isinstance(self.simple_api, KISSimpleDomesticStock):
            self.account_no = self.simple_api.account_no + self.simple_api.account_product_code

        self.logger.info(f"Trading tracker started! Account No: {self.account_no} / save history: {self.save_trading_history}")

        self._fetch_tickers()
        self._sync_positions_and_pending_orders()

        if len(self.pending_orders) > 0:
            self.logger.info("Initial pending orders:")
            for o in self.pending_orders:
                self.logger.info(f"- {o.order_no}({o.org_order_no})\t{o.side}\t{o.asset_code}\t{o.filled_quantity}/{o.quantity}\t{o.is_pending}")

        self.tracker_number = self.tracker_socket.add_tracker(self._handle_order_event)

        self.tasks = [
            asyncio.create_task(self.tracker_socket.start()),
            asyncio.create_task(self._monitor_schedule()),
        ]
        self.started = True

    def enable_save_trading_history(self):
        self.save_trading_history = True

    def _fetch_tickers(self):
        df = get_tickers(dtm.date.today())
        df.reset_index(inplace=True)
        for d in df.to_dict(orient="records"):
            self.tickers[d["code"]] = d

        self.ticker_date = dtm.datetime.now()

        last_trading_day = get_last_trading_day(dtm.date.today())
        last_t_day_df = get_tickers(last_trading_day)
        last_t_day_df.reset_index(inplace=True)

        for d in last_t_day_df.to_dict(orient="records"):
            self.last_t_day_tickers[d["code"]] = d

    def _sync_positions_and_pending_orders(self):
        self.positions = self.simple_api.get_positions()
        for p in self.positions:
            p.current_price = None
            p.current_value = None
            p.current_pnl = None
            p.current_pnl_value = None

        self.pending_orders = self.simple_api.get_pending_orders(exchanges=list(OrderExchange))

    async def stop(self):
        """
        거래 내역 추적을 중지합니다
        """
        for t in self.tasks:
            t.cancel()
        await asyncio.gather(*self.tasks)
        await self.tracker_socket.remove_tracker(self.tracker_number)
        self.started = False

    async def _monitor_schedule(self):
        """거래 시간대별 작업을 위한 스케줄을 모니터링합니다"""
        while not self.tracker_socket.stop_event.is_set():
            market_schedule = get_market_schedule(dtm.date.today())

            if not market_schedule.full_day_closed:
                # 정규장 시작 30분 전 종목정보 갱신
                ticker_fresh_time = (dtm.datetime.combine(dtm.date.today(), market_schedule.open_time) - dtm.timedelta(minutes=30)).time()

                ticker_refresh_seq_no = self._calc_clock_seq(t=ticker_fresh_time)

                # 정규장 종료 시 주문, 포지션 정보 갱신
                market_close_sync_seq_no = self._calc_clock_seq(t=market_schedule.close_time)

                # 시간외 거래 종료 시 주문, 포지션 정보 갱신
                after_market_close_sync_seq_no = self._calc_clock_seq(t=dtm.time(18, 0, 0))

            try:
                seq_no = self._calc_clock_seq()

                if market_schedule.full_day_closed:
                    pass

                elif seq_no == ticker_refresh_seq_no:
                    self._fetch_tickers()
                    self._sync_positions_and_pending_orders()

                elif seq_no == market_close_sync_seq_no:
                    self._sync_positions_and_pending_orders()
                    self.save_positions()

                elif seq_no == after_market_close_sync_seq_no:
                    self._sync_positions_and_pending_orders()

                await asyncio.sleep(60)
            except asyncio.CancelledError:
                return
            except Exception as e:
                self.logger.exception(f"Error on monitoring schedule: {e}")

    def _calc_clock_seq(
        self,
        interval=dtm.timedelta(seconds=60),
        t: dtm.time = None,
    ):
        """현재 시각을 기준으로 시간대별 시퀀스 번호를 계산합니다"""
        midnight = dtm.datetime.combine(dtm.date.today(), dtm.time.min)
        clock_time = dtm.datetime.now() if t is None else dtm.datetime.combine(dtm.date.today(), t)
        elapsed = clock_time - midnight
        return int(elapsed.total_seconds() / interval.total_seconds())

    def _find_pending_order(self, order_no) -> StockOrder:
        return find(lambda x: x.order_no == order_no, self.pending_orders)

    def _find_order_in_today_orders(self, order_no) -> StockOrder:
        today_orders = self.simple_api.get_today_order_history(order_no=order_no, exchanges=[OrderExchange.KRX, OrderExchange.NXT, OrderExchange.SOR])
        return find(lambda x: x.order_no == order_no, today_orders)

    def _find_position(self, asset_code) -> StockPosition:
        return find(lambda x: x.asset_code == asset_code, self.positions)

    def _recalc_average_purchase_price(self, asset_code, quantity, price):
        p = self._find_position(asset_code)
        total_value = price * quantity
        total_quantity = quantity

        if p is not None:
            prev_value = Decimal(p.average_purchase_price * p.quantity)
            total_value += prev_value
            total_quantity += p.quantity

        return Decimal(total_value / total_quantity).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def _handle_order_event(
        self,
        event: OrderEvent,
    ):
        self.logger.debug(
            f"handle_order_event: accno={event.account_no} order_no={event.order_no} (org={event.org_order_no})\tside={event.side}\tcode={event.asset_code}\tfilled={event.filled_quantity}\torder_qty={event.quantity}\tevent_type={event.event_type}"
        )

        if event.account_no != self.account_no:
            return

        if event.event_type == "accepted":
            self._handle_accept_order_event(event)

        elif event.event_type == "cancelled":
            self._handle_cancel_order_event(event)

        elif event.event_type == "executed":
            self._handle_execution_order_event(event)

    def _handle_accept_order_event(self, event: OrderEvent):
        self.logger.debug(f"accept event: order_no={event.order_no} (org={event.org_order_no}) qty={event.quantity} side={event.side}")
        order = StockOrder(
            order_no=event.order_no,
            asset_code=event.asset_code,
            side=event.side,
            order_type=event.order_type,
            quantity=event.quantity,
            price=event.price,
            filled_quantity=0,
            pending_quantity=event.quantity,
            order_time=event.filled_time,
            org_order_no=event.org_order_no,
            exchange=event.exchange,
        )
        self.pending_orders.append(order)

        org_order = self._find_pending_order(event.org_order_no)
        if org_order is not None:
            if org_order.pending_quantity == event.quantity:
                self.pending_orders.remove(org_order)
            else:
                org_order.pending_quantity -= event.quantity

        self._notify_pending_order_update("accepted", order)

        if event.side == OrderSide.SELL:
            position = self._find_position(event.asset_code)
            if position is not None:
                position.sell_possible_quantity -= event.quantity

    def _handle_cancel_order_event(self, event: OrderEvent):
        self.logger.debug(f"cancel event: order_no={event.order_no}")

        order = self._find_pending_order(event.order_no)
        if order is not None:
            self.pending_orders.remove(order)

            order.pending_quantity = 0
            order.is_pending = False

            if event.side == OrderSide.SELL:
                position = self._find_position(event.asset_code)
                if position is not None:
                    position.sell_possible_quantity += order.pending_quantity

            self._notify_pending_order_update("cancelled", order)

    def _handle_execution_order_event(self, event: OrderEvent):
        order_no = event.order_no
        side = event.side
        asset_code = event.asset_code
        total_filled_quantity = event.filled_quantity

        order = self._find_pending_order(event.order_no)
        position = self._find_position(event.asset_code)
        position_event_type = "modified"

        if order:
            order.filled_quantity += event.filled_quantity
            order.pending_quantity -= event.filled_quantity
            total_filled_quantity = order.filled_quantity

        self.logger.debug(f"execution event: order_no={event.order_no} filled={total_filled_quantity} total={event.quantity} filled_price={event.filled_price}")

        if side == OrderSide.SELL:
            if position:
                position.quantity -= event.filled_quantity

                if position.quantity == 0:
                    self.positions.remove(position)
                    position_event_type = "removed"

            else:
                raise Exception("Position not found")

        elif side == OrderSide.BUY:
            if position:
                position.average_purchase_price = self._recalc_average_purchase_price(asset_code, event.filled_quantity, event.filled_price)
                position.quantity += event.filled_quantity
                position.sell_possible_quantity += event.filled_quantity
            else:
                try:
                    asset_info = self.tickers[asset_code]
                except KeyError:
                    self.logger.warn(f"Ticker info not found for asset code: {asset_code}")
                    asset_info = self.last_t_day_tickers.get(asset_code, {})
                position = StockPosition(
                    asset_code=asset_code,
                    asset_name=asset_info.get("name", ""),
                    quantity=event.filled_quantity,
                    sell_possible_quantity=event.filled_quantity,
                    average_purchase_price=Decimal(event.filled_price),
                )
                self.positions.append(position)
                position_event_type = "added"

        partial = event.quantity != total_filled_quantity

        if not partial and order:
            self.pending_orders.remove(order)

        self._save_trading_history(
            asset_code,
            side,
            order_no,
            event.filled_price,
            total_filled_quantity,
            position.average_purchase_price,
            event.filled_time,
            partial,
        )

        if order is None:
            self.logger.warn(f"Order not found for order_no: {order_no}")
            order = self._find_order_in_today_orders(order_no)
            self.logger.warn(f"Order found in today's orders: {order}")
        self._notify_pending_order_update("partial" if partial else "completed", order)
        self._notify_position_update(position_event_type, position)

    def _refresh_positions(self):
        self.positions = self.simple_api.get_positions()

    def _refresh_pending_orders(self):
        self.pending_orders = self.simple_api.get_pending_orders(exchanges=list(OrderExchange))

    def _notify_pending_order_update(self, status: str, order: StockOrder):
        # deprecated
        if self.on_pending_order_update is not None:
            self.on_pending_order_update(status, order)

        for callback in self.on_pending_order_update_callback_dict.values():
            callback(status, order)

    def _notify_position_update(self, type: str, position: StockPosition = None):
        # deprecated
        if self.on_position_update is not None:
            self.on_position_update(type, position)

        for callback in self.on_position_update_callback_dict.values():
            callback(type, position)

    def add_pending_order_update_callback(self, callback, callback_id=None):
        if callback_id is None:
            callback_id = self.callback_id
            self.callback_id += 1

        self.on_pending_order_update_callback_dict[callback_id] = callback
        return callback_id

    def remove_pending_order_update_callback(self, callback_id):
        if callback_id is not None and callback_id in self.on_pending_order_update_callback_dict:
            del self.on_pending_order_update_callback_dict[callback_id]

    def add_position_update_callback(self, callback, callback_id=None):
        if callback_id is None:
            callback_id = self.callback_id
            self.callback_id += 1

        self.on_position_update_callback_dict[callback_id] = callback
        return callback_id

    def remove_position_update_callback(self, callback_id):
        if callback_id is not None and callback_id in self.on_position_update_callback_dict:
            del self.on_position_update_callback_dict[callback_id]

    def _save_trading_history(
        self,
        asset_code: str,
        side: OrderSide,
        order_no: str,
        filled_price: int,
        filled_quantity: int,
        average_purchase_price: Decimal = None,
        executed_time: dtm.datetime = None,
        partial: bool = False,
    ):

        try:
            asset_info = self.tickers[asset_code]
        except KeyError:
            self.logger.warn(f"[_save_trading_history] Ticker info not found for asset code: {asset_code}")
            asset_info = self.last_t_day_tickers.get(asset_code, {})
        is_equity = asset_info.get("type", "EQUITY") == "EQUITY"
        fee = filled_price * filled_quantity * self.fee_rate
        tax = 0
        pnl = None
        pnl_rate = None

        if side == OrderSide.SELL:
            sell_value = filled_price * filled_quantity
            if is_equity:
                tax = sell_value * self.tax_rate
            buy_value = average_purchase_price * filled_quantity
            buy_fee = buy_value * self.fee_rate
            pnl = sell_value - buy_value - fee - tax - buy_fee
            pnl_rate = pnl / buy_value * 100 if buy_value != 0 else 0

        data = TradingHistory(
            date=dtm.date.today().strftime("%Y%m%d"),
            order_no=order_no,
            side="buy" if side == OrderSide.BUY else "sell",
            asset_code=asset_code,
            quantity=filled_quantity,
            filled_price=filled_price,
            average_purchase_price=float(average_purchase_price),
            tax=float(tax) if tax is not None else None,
            fee=float(fee) if fee is not None else None,
            pnl=float(pnl) if pnl is not None else None,
            pnl_rate=float(pnl_rate) if pnl_rate is not None else None,
            executed_time=(int(executed_time.timestamp() * 1000) if executed_time else None),
            partial=partial,
        )

        self._send_trading_history(data)

    def _send_trading_history(self, history: TradingHistory):
        if not self.save_trading_history:
            return

        url = f"{c.PYQQQ_API_URL}/analytics/trades/{history.order_no}"

        data = asdict(history)
        data["brokerage"] = "ebest" if isinstance(self.simple_api, EBestSimpleDomesticStock) else "kis"
        data["account_no"] = self.account_no

        strategy_name = os.getenv("STRATEGY_NAME")
        if strategy_name is not None:
            data["strategy_name"] = strategy_name

        positions = []
        for p in self.positions:
            d = asdict(p)
            d["average_purchase_price"] = float(d["average_purchase_price"])
            positions.append(d)

        r = send_request("POST", url, json=data)
        raise_for_status(r)

        self.logger.info(f"save trading history: {data}")

    def save_positions(self):
        if not self.save_trading_history:
            return

        strategy_name = os.getenv("STRATEGY_NAME")
        if strategy_name is None:
            return

        url = f"{c.PYQQQ_API_URL}/analytics/positions"

        positions = []

        for p in self.simple_api.get_positions():
            d = asdict(p)
            d["average_purchase_price"] = float(d["average_purchase_price"])
            d["current_pnl"] = float(d["current_pnl"]) if "current_pnl" in d else None
            positions.append(d)

        account = self.simple_api.get_account()
        account["pnl_rate"] = float(account["pnl_rate"]) if "pnl_rate" in account else None

        req_body = {
            "date": dtm.date.today().strftime("%Y%m%d"),
            "brokerage": ("ebest" if isinstance(self.simple_api, EBestSimpleDomesticStock) else "kis"),
            "account_no": self.account_no,
            "positions": positions,
            "account": account,
            "strategy_name": strategy_name,
        }

        print(req_body)

        r = send_request("POST", url, json=req_body)
        raise_for_status(r)

        self.logger.info(f"save positions: {positions}")
