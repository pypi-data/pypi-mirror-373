from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.utils.logger import get_logger
from pyqqq.utils.retry import retry
from typing import AsyncGenerator, Callable
import asyncio
import random
import requests
import ssl
import websockets


class KISTRClient:
    logger = get_logger(__name__ + ".KISTRClient")

    """
    한국투자증권 TR 요청을 위한 클라이언트

    Args:
        auth (KISAuth): 인증 정보를 담고 있는 객체
        corp_data (dict): 기업 고객의 경우 추가로 필요한 정보를 담고 있는 객체
    """

    def __init__(self, auth: KISAuth, corp_data: dict = None):
        self.auth = auth
        self.corp_data = corp_data
        self.session = requests.Session()

    @retry(requests.RequestException)
    def request(self, path: str, tr_id: str, tr_cont: str = "", params: dict = None, body: dict = None, method: str = "GET"):
        """
        TR 요청을 보내고 응답을 받는 메서드

        Args:
            path (str): 요청을 보낼 URL 경로
            tr_id (str): TR ID
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
            "appkey": self.auth.appkey,
            "appsecret": self.auth.appsecret,
            "custtype": "P" if self.corp_data is None else "B",
            "tr_id": tr_id,
            "tr_cont": tr_cont,
        }
        if self.corp_data is not None:
            headers.update(self.corp_data)

        url = f"{self.auth.host_url}{path}"

        r = self.session.request(method=method, url=url, headers=headers, params=params, json=body)

        if r.status_code != 200:
            try:
                res_body = r.json()
                if "msg_cd" in res_body and res_body["msg_cd"] == "EGW00123":
                    self.auth.get_token(True)

            except Exception as e:
                self.logger.exception(e)
            print(r.text)
            r.raise_for_status()

        response_headers = r.headers
        response_body = r.json()

        return response_body, response_headers


class KISTRWebsocketClient:
    """
    한국투자증권 실시간 데이터 수신을 위한 웹소켓 클라이언트

    Args:
        auth (KISAuth): 인증 정보를 담고 있는 객체
        on_connect (Callable): 웹소켓 연결 시 실행할 콜백 함수
        stop_event (asyncio.Event): 종료 이벤트
    """

    logger = get_logger(__name__ + ".KISTRWebsocketClient")

    def __init__(
        self,
        auth: KISAuth,
        on_connect: Callable = None,
        stop_event: asyncio.Event = None,
    ):
        self.auth = auth
        self.on_connect = on_connect
        self.stop_event = stop_event or asyncio.Event()
        self.session_id = self.make_session_id()
        self.iv = None
        self.key = None

    def make_session_id(self) -> str:
        """세션 ID 생성

        Returns:
            영문자 + 숫자 형식 12자리 문자열
        """
        return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=12))

    async def listen(self) -> AsyncGenerator:
        """
        웹소켓 연결을 유지하고 데이터를 수신하는 메서드

        Yields:
            dict: 수신한 데이터
        """
        websocket_url = f"{self.auth.websocket_url}"

        while not self.stop_event.is_set():
            try:
                async with websockets.connect(websocket_url) as ws:
                    if self.on_connect:
                        await self.on_connect(ws)

                    while not self.stop_event.is_set():
                        data = await self.recv_with_timeout(ws, timeout=1)

                        if data:
                            yield data

            except websockets.exceptions.ConnectionClosedError:
                self.logger.error(f"{self.session_id}: ConnectionClosedError")
                await asyncio.sleep(0.5)
                continue

            except ConnectionRefusedError:
                self.logger.error(f"{self.session_id}: ConnectionRefusedError")
                await asyncio.sleep(0.5)
                continue

            except websockets.ConnectionClosed:
                self.logger.error(f"{self.session_id}: ConnectionClosed")
                await asyncio.sleep(0.5)
                continue

            except ssl.SSLZeroReturnError:
                self.logger.error(f"{self.session_id}: SSLZeroReturnError")
                await asyncio.sleep(0.5)
                continue

            except Exception as e:
                # any other exceptions
                self.logger.exception(e)
                await asyncio.sleep(1)
                continue

    async def recv_with_timeout(self, ws: websockets.WebSocketClientProtocol, timeout: int = 1) -> str:
        """timeout 초 동안 수신을 대기하고 수신이 없으면 None을 반환한다"""
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout)
            return message
        except asyncio.TimeoutError:
            return None

    def stop(self):
        """
        웹소켓 연결을 종료하는 메서드
        """
        if not self.stop_event.is_set():
            self.stop_event.set()
