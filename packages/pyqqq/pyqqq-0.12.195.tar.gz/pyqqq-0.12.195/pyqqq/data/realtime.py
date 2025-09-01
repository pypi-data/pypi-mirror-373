import asyncio
import datetime as dtm
import inspect
import json
import os
from typing import List, Union

import websockets

import pyqqq.config as c
from pyqqq.datatypes import DataExchange, Exchange
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.logger import get_logger
from pyqqq.utils.singleton import singleton
from pyqqq.utils.market_schedule import is_trading_time, get_next_trading_day, get_market_schedule

logger = get_logger(__name__)


def get_all_last_trades(
    codes: List[str] = None,
    exchange: Union[str, DataExchange] = "KRX",
):
    """
    모든 종목의 최근 체결 정보를 반환합니다.

    Note:
        - KRX, UN 거래소의 최근 체결 정보를 조회할 수 있습니다. NXT 거래소는 지원되지 않습니다.

    Args:
        codes (List[str], optional): 종목 코드 리스트. 모든 종목의 체결 정보를 반환하려면 None을 전달합니다.
        exchange (str): 거래소. 기본값은 "KRX"입니다. 지원하는 거래소는 "KRX", "UN" 입니다.

    Returns:
        list:
        - dict:
            - sign (int): 전일대비구분
            - change (int): 전일대비가격
            - drate (float): 전일대비등락율
            - price (int): 체결가
            - open (int): 시가
            - high (int): 고가
            - low (int): 저가
            - cgubun (str): 체결구분
            - cvolume (int): 체결량
            - volume (int): 누적거래량
            - value (int): 누적거래대금(백만)
            - mdvolume (int): 매도체결수량
            - mdchecnt (int): 매도체결건수
            - msvolume (int): 매수체결수량
            - mschecnt (int): 매수체결건수
            - cpower (float): 체결강도
            - offerho (int): 매도호가
            - bidho (int): 매수호가
            - status (str): 장정보
            - jnilvolume (int): 전일동시간대거래량
            - shcode (str): 종목코드
            - exchname (str): 거래소명
            - date (str): 체결일자
            - update_time (str): 업데이트 시간

    Raises:
        ValueError: 지원하지 않는 거래소 코드가 전달된 경우.
    """
    exchange = DataExchange.validate(exchange)
    if exchange == DataExchange.NXT:
        raise ValueError("NXT 거래소는 지원되지 않습니다.")

    params = {"exchange": exchange.value}
    if codes:
        params["codes"] = ",".join(codes) if isinstance(codes, list) else codes

    r = send_request("GET", f"{c.PYQQQ_API_URL}/domestic-stock/trades", params=params)
    raise_for_status(r)

    data = r.json()
    result = [data[k] for k in data.keys()]

    return result


def get_all_last_orderbooks():
    """
    모든 종목의 최근 호가 정보를 반환합니다.

    Returns:
        list:
        - dict:
            - hotime (str): 호가 시간 (HHMMSS)
            - date (str): 호가 날짜 (YYYYMMDD)
            - bidho[1~10] (int): 매도 호가
            - bidrem[1~10] (int): 매도 호가 잔량
            - totbidrem (int): 총 매수 호가 잔량
            - offerho[1~10] (int): 매수 호가
            - offerrem[1~10] (int): 매수 호가 잔량
            - totofferrem (int): 총 매수 호가 잔량
            - donsigubun (str): 동시 호가 구분
            - alloc_gubun (str or None): 배분 적용 구분
            - volume (int): 누적 거래량
            - shcode (str): 종목 코드

    """

    r = send_request("GET", f"{c.PYQQQ_API_URL}/domestic-stock/orderbooks")
    raise_for_status(r)

    data = r.json()
    result = [data[k] for k in data.keys()]

    return result


@singleton
class TickEventListener:
    """
    틱 데이터를 실시간으로 구독하는 서버와 websocket으로 연결되오,
    원하는 조건이 충족되었을 때 콜백을 호출하는 클래스입니다.

    객체를 생성 후, start() 하면 웹소켓이 연결됩니다.
    start() 전, 후에 관계없이 append_event()로 이벤트를 추가할 수 있습니다.

    Args:
        client_id (str): 클라이언트 ID. 고유한 값이어야 합니다.
        url (str): 웹소켓 서버 주소. TICKEVENT_URL 환경변수로 설정할 수 있습니다.
        config (dict): 설정값
            event_add_delay (float): 이벤트 추가 딜레이 시간. 기본값은 1초입니다.
    """

    LOG_TAG = "[TickEventListener]"

    def __init__(self, client_id, url=None, config={}):
        self.ws_connected = False
        self.events = {}
        self.pending_event_ids = []
        self.event_add_delay = 1.0
        self.health_ping_delay = 60
        self.retry_cnt = 0
        self.ws = None
        self.tot_retry_cnt = 0
        self.reconnect_datetime = None
        logger.info(f"{self.LOG_TAG}init")

        if "event_add_delay" in config:
            self.event_add_delay = config["event_add_delay"]

        if "health_ping_delay" in config:
            self.health_ping_delay = config["health_ping_delay"]
        now_int_str = str(int(dtm.datetime.now().timestamp()))
        if client_id is not None:
            api_key = os.getenv("PYQQQ_API_KEY") or ""
            self.client_id = client_id + api_key + "_" + now_int_str
        else:
            self.client_id = api_key + "_" + now_int_str

        self.url = url
        if self.url is None:
            self.url = os.getenv("TICKEVENT_URL") or c.PYQQQ_EVENT_WS_URL

    async def start(self):
        """
        틱데이터 이벤트 리스너를 시작합니다
        """
        self.tasks = [asyncio.create_task(self.connect_ws()), asyncio.create_task(self.health_ping())]

    async def stop(self):
        """
        틱데이터 이벤트 리스너를 종료합니다.
        """
        for t in self.tasks:
            t.cancel()

        await asyncio.gather(*self.tasks)

    async def connect_ws(self):
        """
        웹소켓 서버에 연결하여 틱데이터 이벤트를 수신합니다.
        """
        try:
            async with websockets.connect(self.url) as websocket:
                self.retry_cnt = 0
                self.ws_connected = True
                self.ws = websocket

                await self.register(websocket)
                asyncio.create_task(self.process_events_appending())

                try:
                    async for message in websocket:
                        # logger.debug(f"{self.LOG_TAG}message: {message}")
                        await self.handle_response(message)

                    logger.warning(f"{self.LOG_TAG}Websocket connection closed by server. code: {websocket.close_code}, reason: {websocket.close_reason}")
                except websockets.exceptions.ConnectionClosed:
                    logger.info(f"{self.LOG_TAG}Connection closed")
                    if websocket.close_code == 4409:
                        logger.info(f"{self.LOG_TAG}Connection closed by server with code: {websocket.close_code}, reason: {websocket.close_reason}")

                        self.move_events_to_pending()

                        if is_trading_time(dtm.datetime.now()):
                            logger.info("try reconnect next minute")
                            self.reconnect_datetime = dtm.datetime.now() + dtm.timedelta(minutes=1)
                        else:
                            logger.info("not trading time")
                            next_trading_day = get_next_trading_day(dtm.datetime.now().date())
                            next_market_schedule = get_market_schedule(next_trading_day, Exchange.NXT)
                            next_start_time = dtm.datetime.combine(next_trading_day, next_market_schedule.open_time)
                            logger.info(f"reconnect at {next_start_time}")
                            self.reconnect_datetime = next_start_time
                        
                        await asyncio.sleep(self.reconnect_datetime.timestamp() - dtm.datetime.now().timestamp())

                        await self.connect_ws()

                    else:
                        await self.on_connect_failed()
        except Exception as e:
            logger.info(f"{self.LOG_TAG}Connection failed. error: {e}")
            await self.on_connect_failed()
        finally:
            logger.info(f"{self.LOG_TAG}Websocket connection closed")
            self.ws_connected = False

    async def health_ping(self):
        """
        웹소켓 서버에 헬스체크를 보냅니다.
        """
        if self.ws_connected:
            await self.ws.send(json.dumps({"type": "ping", "client_id": self.client_id}))
        await asyncio.sleep(self.health_ping_delay)

    async def on_connect_failed(self):
        self.ws_connected = False
        self.move_events_to_pending()
        self.retry_cnt += 1

        sleep_time = min(60, self.retry_cnt * 2)

        logger.info(f"{self.LOG_TAG}retry cnt: {self.retry_cnt}. sleep_time: {sleep_time} sec")
        await asyncio.sleep(self.retry_cnt * 2)
        await self.connect_ws()

    def append_event(self, ticker, event_id, price, once, side, price_comparison, listen_callback, is_unified=False):
        """
        사용자로부터 틱데이터 이벤트 추가 요청을 등록합니다. 즉시 처리되진 않습니다.

        Args:
            ticker (str): 종목 코드
            event_id (str): 이벤트 ID. 고유한 값이어야 합니다.
            price (int): 가격
            once (bool): 한번만 실행할지 여부
            side (int | OrderSide): 매도/매수 구분 (0: all, 1: sell[cgubun: "-"], 2: buy[cgubun: "+"]) default: 0
            price_comparison (str): 가격 비교 방식 ("<", "<=", "==", ">=", ">")
            listen_callback (callable): 이벤트 발생시 호출할 콜백 함수
            is_unified (bool): 통합 이벤트인지 여부. 기본값은 False입니다.
        """
        self.events[event_id] = TickEvent(
            ticker=ticker, event_listener=self, client_id=self.client_id, event_id=event_id, price=price, once=once, side=side, price_comparison=price_comparison, listen_callback=listen_callback, is_unified=is_unified
        )
        self.pending_event_ids.append(event_id)

    async def append_event_async(self, ticker, event_id, price, once, side, price_comparison, listen_callback, is_unified=False):
        """
        사용자로부터 틱데이터 이벤트 추가 요청을 등록합니다. 비동기로 가능한 한 즉시 처리됩니다.
        """
        if self.ws_connected:
            self.events[event_id] = TickEvent(
                ticker=ticker, event_listener=self, client_id=self.client_id, event_id=event_id, price=price, once=once, side=side, price_comparison=price_comparison, listen_callback=listen_callback, is_unified=is_unified
            )
            logger.info(f"{self.LOG_TAG}append_event_async {event_id}")
            await self.send_subscribe(event_id)
        else:
            logger.info(f"{self.LOG_TAG}append_event_async {event_id} failed")
            self.append_event(ticker, event_id, price, once, side, price_comparison, listen_callback, is_unified)

    async def close_event(self, event_id):
        """
        사용자로부터 틱데이터 이벤트 삭제 요청을 등록합니다. 비동기로 가능한 한 즉시 처리됩니다.
        """
        await self.send_unsubscribe(event_id)

        self.remove_event(event_id)

    async def send_subscribe(self, event_id):
        """
        틱데이터 이벤트 구독 요청을 보냅니다.
        """
        event = self.events[event_id]

        if event is not None and not event.check_removed():
            dumpdata = self.events[event_id].get_subscribe_dump_data()
            await self.ws.send(dumpdata)

    async def send_unsubscribe(self, event_id):
        """
        틱데이터 이벤트 구독 해지 요청을 보냅니다.
        """
        event = self.events[event_id]

        if event is not None and not event.check_removed():
            dumpdata = event.get_unsubscribe_dump_data()
            await self.ws.send(dumpdata)
            event.remove_event()

    def remove_event(self, event_id):
        """
        특정 이벤트를 리스너에서 삭제합니다.
        사용자가 직접 호출하는건 권장하지 않습니다.
        """

        if event_id in self.events:
            event = self.events[event_id]
            del self.events[event_id]
            del event

        if event_id in self.pending_event_ids:
            self.pending_event_ids.remove(event_id)

    async def process_events_appending(self):
        """
        사용자로부터 받았던 틱데이터 이벤트 요청을 모아서 처리합니다.
        웹소켓 연결 해제 후 재연결시에서도 사용됩니다.
        """
        self.tot_retry_cnt += 1
        cur_retry_cnt = self.tot_retry_cnt
        logger.info(f"{self.LOG_TAG} process_events_appending")
        while True:
            if cur_retry_cnt < self.tot_retry_cnt:
                logger.info(f"{self.LOG_TAG} old process task exit. {cur_retry_cnt}, {self.tot_retry_cnt}")
                return
            if self.ws_connected:
                res = []
                # 날짜가 바뀌면 이벤트를 모두 날립니다
                keys = list(self.events.keys())
                for event_id in keys:
                    if self.events[event_id].check_day_changed():
                        await self.close_event(event_id)

                cur_pending_event_ids = list(self.pending_event_ids)
                for pending_event_id in cur_pending_event_ids:
                    if not self.events[pending_event_id].check_removed():
                        await self.send_subscribe(pending_event_id)
                        res.append(pending_event_id)
                    self.pending_event_ids.remove(pending_event_id)

                if len(res) > 0 or len(cur_pending_event_ids) > 0:
                    logger.debug(f"{self.LOG_TAG} try connect events:{cur_pending_event_ids}, connected: {res}")

            else:
                logger.info(f"{self.LOG_TAG} not connected. stop process_events_appending")
                return

            await asyncio.sleep(self.event_add_delay)

    def move_events_to_pending(self):
        self.pending_event_ids = list(self.events.keys())

    async def register(self, ws):
        """
        서버에 유저를 등록합니다.
        """
        data = json.dumps({"type": "register", "client_id": self.client_id})
        logger.info(f"{self.LOG_TAG}registering. data:{data}")
        await ws.send(data)

    async def handle_response(self, response):
        """
        서버로부터 받은 틱데이터 이벤트를 처리합니다.
        """
        data = json.loads(response)
        if "event_id" not in data:
            # res_data = data["data"]
            # if res_data["message"] == "pong":
            #     logger.debug(f"{self.LOG_TAG} pong response")
            return

        event_id = data["event_id"]
        if event_id in self.events:
            event = self.events[event_id]
            if event.check_removed():
                self.events.remove(event_id)
                return
            else:
                await event.handle_tick_data(data)
        else:
            logger.warning(f"{self.LOG_TAG}event_id {event_id} not found")


class TickEvent:
    """
    TickEventListener 클래스에서 사용하는 틱데이터 이벤트 클래스입니다.
    """

    LOG_TAG = "[TickEvent]"
    CLOSE_TIME = dtm.time(18, 0)

    def __init__(self, event_listener, ticker, client_id, event_id, price, once, side, price_comparison, listen_callback, is_unified=False):
        logger.info(f"{self.LOG_TAG} create {event_id}, {ticker}, {price}, {price_comparison}")
        self.removed = False
        self.event_listener = event_listener
        self.ticker = ticker
        self.client_id = client_id
        self.event_id = event_id
        self.price = price
        self.once = once
        self.side = side
        self.price_comparison = price_comparison
        self.listen_callback = listen_callback
        self.is_unified = is_unified  # 통합 이벤트인지 여부

        self.date = dtm.datetime.now().strftime("%Y%m%d")

    def get_subscribe_dump_data(self):
        logger.info(f"{self.LOG_TAG} subscribe {self.event_id}, {self.ticker}, {self.price}, {self.price_comparison}, {self.side}")

        ticker = "U" + self.ticker if self.is_unified else self.ticker

        return json.dumps({"type": "subscribe", "ticker": ticker, "client_id": self.client_id, "event_id": self.event_id, "price": self.price, "once": self.once, "side": self.side, "price_comparison": self.price_comparison})

    def get_unsubscribe_dump_data(self):
        ticker = "U" + self.ticker if self.is_unified else self.ticker

        return json.dumps({"type": "unsubscribe", "ticker": ticker, "client_id": self.client_id, "event_id": self.event_id})

    async def handle_tick_data(self, data):
        if self.listen_callback:
            if inspect.iscoroutinefunction(self.listen_callback):
                await self.listen_callback(data)
            else:
                self.listen_callback(data)

        if self.once:
            self.remove_event()
            self.event_listener.remove_event(self.event_id)

    def remove_event(self):
        self.removed = True

    def check_removed(self):
        return self.removed

    def check_day_changed(self):
        now = dtm.datetime.now()
        if self.date != now.strftime("%Y%m%d"):
            return True
        else:
            if now.time() >= self.CLOSE_TIME:
                return True
            else:
                return False
