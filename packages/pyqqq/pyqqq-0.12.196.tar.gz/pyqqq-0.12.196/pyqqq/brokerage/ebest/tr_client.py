from enum import Enum
from pyqqq.brokerage.ebest.oauth import EBestAuth
from pyqqq.utils.logger import get_logger
from pyqqq.utils.market_schedule import *
from pyqqq.utils.retry import retry
from typing import AsyncGenerator, Callable
import asyncio
import json
import ssl
import random
import requests
import websockets


class EBestTRClient:
    logger = get_logger(__name__ + ".EBestTRClient")

    """
    한국투자증권 TR 요청을 위한 클라이언트

    Args:
        auth (KISAuth): 인증 정보를 담고 있는 객체
        corp_data (dict): 기업 고객의 경우 추가로 필요한 정보를 담고 있는 객체
    """

    def __init__(self, auth: EBestAuth, corp_data: dict = None):
        self.auth = auth
        self.corp_data = corp_data

    @retry(requests.HTTPError)
    def request(
        self,
        path: str,
        tr_cd: str,
        tr_cont: str = "N",
        tr_cont_key: str = "",
        params: dict = None,
        body: dict = None,
        method: str = "POST",
    ):
        """
        TR 요청을 보내고 응답을 받는 메서드

        Args:
            path (str): 요청을 보낼 URL 경로
            tr_cd (str): TR ID
            tr_cont (str): TR CONT
            params (dict): URL 쿼리 파라미터
            body (dict): 요청 바디
            method (str): HTTP 메서드

        Returns:
            tuple: 응답 바디와 응답 헤더를 담은 튜플

        Raises:
            requests.HTTPError: 요청이 실패한 경우
        """
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.auth.get_token()}",
            "tr_cd": tr_cd,
            "tr_cont": tr_cont,
            "tr_cont_key": tr_cont_key,
        }
        if self.corp_data is not None:
            headers.update(self.corp_data)

        url = f"{self.auth.host_url}{path}"

        r = requests.request(method=method, url=url, headers=headers, params=params, json=body)

        if r.status_code != 200:
            try:
                res_body = r.json()
                if "rsp_cd" in res_body and res_body["rsp_cd"] == "IGW00121":
                    self.auth.get_token(refresh=True)
            except Exception as e:
                self.logger.exception(e)

            print(r.text)
            r.raise_for_status()

        response_headers = r.headers
        response_body = r.json()

        return response_body, response_headers


class EBestTRWebsocketKeepConnectionStatus(Enum):
    """
    LS(구 이베스트투자)증권 TR 요청 웹소켓 클라이언트의 연결 유지 상태
    """

    WAIT = "wait"
    """ 대기 """
    KEEP = "keep"
    """ 유지 """
    CLOSE = "close"
    """ 종료 """


class EBestTRWebsocketClient:
    """
    LS(구 이베스트투자)증권 실시간 데이터 요청을 위한 웹소켓 클라이언트

    Args:
        auth (KISAuth): 인증 정보를 담고 있는 객체
        on_connect (Callable): 웹소켓 연결 시 호출할 콜백 함수
        on_ask_keep_connection (Callable): 연결 유지 여부를 묻는 메시지를 받았을 때 호출할 콜백 함수. 'wait', 'keep', 'close' 중 하나를 반환해야 함
        stop_event (asyncio.Event): 종료 이벤트
    """

    logger = get_logger(__name__ + ".EBestTRWebsocketClient")

    def __init__(
        self,
        auth: EBestAuth,
        on_connect: Callable[[websockets.WebSocketClientProtocol], asyncio.Task] = None,
        on_ask_keep_connection: Callable[[], EBestTRWebsocketKeepConnectionStatus] = lambda: EBestTRWebsocketKeepConnectionStatus.KEEP,
        stop_event: asyncio.Event = None,
    ):

        self.auth = auth
        self.task = None
        self.on_connect = on_connect
        self.on_ask_keep_connection = on_ask_keep_connection
        self.stop_event = stop_event or asyncio.Event()
        self.session_id = self.make_session_id()

    def make_session_id(self) -> str:
        """세션 ID 생성

        Returns:
            영문자 + 숫자 형식 12자리 문자열
        """
        return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=12))

    async def listen(self) -> AsyncGenerator:
        """
        웹소켓을 통해 실시간 데이터를 수신하는 메서드

        Yields:
            dict: 실시간 데이터

        """
        websocket_url = f"{self.auth.websocket_url}/websocket"

        while not self.stop_event.is_set():
            try:
                keep_connection = self.on_ask_keep_connection()

                if keep_connection == EBestTRWebsocketKeepConnectionStatus.CLOSE:
                    break

                elif keep_connection == EBestTRWebsocketKeepConnectionStatus.WAIT:
                    await asyncio.sleep(0.5)
                    continue

                async with websockets.connect(websocket_url) as ws:
                    self.logger.info(f"{self.session_id}: connected to websocket")
                    if self.on_connect:
                        await self.on_connect(ws)

                    while not self.stop_event.is_set():
                        data = await self.recv_with_timeout(ws, timeout=1)
                        if data:
                            json_data = json.loads(data)
                            if json_data.get("body") is not None:
                                yield json_data

                            else:
                                if json_data["header"]["rsp_cd"] != "00000":
                                    self.logger.warn(json_data)

                        elif self.on_ask_keep_connection() == EBestTRWebsocketKeepConnectionStatus.CLOSE:
                            break

                        await asyncio.sleep(0.01)

            except websockets.exceptions.ConnectionClosedError:
                self.logger.error(f"{self.session_id}: ConnectionClosedError")
                await asyncio.sleep(0.5)
                continue

            except websockets.ConnectionClosed as e:
                await asyncio.sleep(0.5)
                self.logger.exception(e)
                continue

            except ssl.SSLZeroReturnError:
                self.logger.error(f"{self.session_id}: SSLZeroReturnError")
                await asyncio.sleep(0.5)
                continue

            except TimeoutError as e:
                self.logger.exception(e)
                await asyncio.sleep(1)
                continue

            except Exception as e:
                # any other exception
                self.logger.exception(e)
                await asyncio.sleep(1)
                continue

    def is_safe_to_close(self) -> bool:
        now = dtm.datetime.now()
        today = now.date()
        schedule = get_market_schedule(today)
        if schedule.full_day_closed:
            return True

        close_time = dtm.datetime.combine(today, schedule.close_time)
        safe_close_time = close_time + dtm.timedelta(hours=2, minutes=35)
        return now > safe_close_time

    def is_before_opening(self) -> bool:
        now = dtm.datetime.now()
        today = now.date()
        schedule = get_market_schedule(today)
        if schedule.full_day_closed:
            return True

        open_time = dtm.datetime.combine(today, schedule.open_time)
        safe_listen_time = open_time - dtm.timedelta(minutes=31)
        return now < safe_listen_time

    async def recv_with_timeout(self, ws: websockets.WebSocketClientProtocol, timeout: int = 1) -> str:
        """timeout 초 동안 수신을 대기하고 수신이 없으면 None을 반환한다"""
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout)
            return message
        except asyncio.TimeoutError:
            return None

    def stop(self):
        if not self.stop_event.is_set():
            self.stop_event.set()
