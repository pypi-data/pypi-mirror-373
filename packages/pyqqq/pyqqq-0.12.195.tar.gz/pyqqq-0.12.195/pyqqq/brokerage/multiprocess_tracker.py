from decimal import Decimal
from pyqqq.brokerage.ebest.oauth import EBestAuth
from pyqqq.brokerage.ebest.simple import EBestSimpleDomesticStock
from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.brokerage.kis.simple import KISSimpleDomesticStock
from pyqqq.brokerage.tracker import TradingTracker
from pyqqq.datatypes import *
from pyqqq.utils.logger import get_logger
from typing import Dict
import asyncio
import multiprocessing


class TradingTrackerMultiProcessController:
    """
        부모 프로세스에서 생성되는 TradingTracker Controller
        메시지 큐를 통해 자식 프로세스에서 돌아가는 TradingTracker를 제어한다.
        자식 프로세스에서 listen한 order 이벤트는 event_snapshot_queue를 통해 받을 수 있다.
    """

    def __init__(
        self,
        auth_info: Dict[str, str] = None,
        fee_rate: Decimal = Decimal("0.00015"),  # 뱅키스, LS증권 수수료율 0.015%
    ):

        self.auth_info = auth_info
        self.fee_rate = fee_rate
        self.event_snapshot_queue = multiprocessing.Queue()
        self.message_queue = multiprocessing.Queue()

    def start(self):
        print("process controller. start called")
        self.process = multiprocessing.Process(target=run_subprocess, args=(self.fee_rate, self.event_snapshot_queue, self.message_queue, self.auth_info))
        self.process.start()

    def stop(self):
        print("process controller. stop called")
        if self.process is not None:
            self.message_queue.put("stop")
            self.process.join()

            print("process controller. process joined")

    def get_event_snapshot(self):
        if not self.event_snapshot_queue.empty():
            return self.event_snapshot_queue.get()
        return None


class TradingTrackerMultiProcessWorker:
    """
        자식 프로세스에서만 생성되는 TradingTracker Worker

    Args:
        event_snapshot_queue (multiprocessing.Queue): 거래 이벤트가 발생시, 부모 프로세스에 스냅샷을 전송하는 큐
        message_queue (multiprocessing.Queue): 부모 프로세스에서 명령을 전달할때 사용하는 큐
        fee_rate (Decimal): 증권사 수수료율 (기본값: 0.015%)
    """

    logger = get_logger(__name__ + ".TradingTrackerMultiProcessWorker")

    def __init__(
        self,
        event_snapshot_queue: multiprocessing.Queue,
        message_queue: multiprocessing.Queue,
        auth_info: Dict[str, str] = {},
        fee_rate: Decimal = Decimal("0.00015"),  # 뱅키스, LS증권 수수료율 0.015%
    ):
        print("TradingTrackerMultiProcessWorker init")
        self.event_snapshot_queue = event_snapshot_queue
        self.message_queue = message_queue
        self.stop_event = asyncio.Event()

        # auth_info를 외부에서 넣어주는 경우
        if auth_info is not None:
            if "KIS_APP_KEY" in auth_info:
                self.auth = KISAuth(
                    appkey=auth_info["KIS_APP_KEY"],
                    appsecret=auth_info["KIS_APP_SECRET"],
                    paper_trading=auth_info["PAPER_TRADING"] == "1",
                )

                self.simple_api = KISSimpleDomesticStock(
                    auth=self.auth,
                    account_no=auth_info["KIS_CANO"],
                    account_product_code=auth_info["KIS_ACNT_PRDT_CD"],
                    hts_id=auth_info["KIS_HTS_ID"],
                )
            elif "EBEST_APP_KEY" in auth_info:
                self.auth = EBestAuth(
                    auth_info["EBEST_APP_KEY"],
                    auth_info["EBEST_APP_SECRET"],
                    paper_trading=auth_info["PAPER_TRADING"] == "1",
                )
                self.simple_api = EBestSimpleDomesticStock(auth=self.auth)

        else:
            if os.getenv("EBEST_APP_KEY") is not None and os.getenv("KIS_APP_KEY") is None:
                self.auth = EBestAuth(
                    os.getenv("EBEST_APP_KEY"),
                    os.getenv("EBEST_APP_SECRET"),
                    paper_trading=os.getenv("PAPER_TRADING") == "1",
                )
                self.simple_api = EBestSimpleDomesticStock(auth=self.auth)

            else:
                self.auth = KISAuth(
                    appkey=os.getenv("KIS_APP_KEY"),
                    appsecret=os.getenv("KIS_APP_SECRET"),
                    paper_trading=os.getenv("PAPER_TRADING") == "1",
                )

                self.simple_api = KISSimpleDomesticStock(
                    auth=self.auth,
                    account_no=os.getenv("KIS_CANO"),
                    account_product_code=os.getenv("KIS_ACNT_PRDT_CD"),
                    hts_id=os.getenv("KIS_HTS_ID"),
                )
        self.tracker = TradingTracker(self.simple_api, fee_rate=fee_rate)
        self.tracker.add_pending_order_update_callback(self.on_pending_order_update)

    async def start(self):
        """
        Tracker와 메시지 큐 리스너를 시작합니다
        """
        self.tasks = [
            asyncio.create_task(self.tracker.start()),
            asyncio.create_task(self._listen_message_queue()),
        ]
        await asyncio.gather(*self.tasks)

    async def stop(self):
        """
        Tracker와 메시지 큐 리스터를 중단합니다.
        """
        self.stop_event.set()
        await self.tracker.stop()
        for t in self.tasks:
            t.cancel()

        await asyncio.gather(*self.tasks)

    async def _listen_message_queue(self):
        """
        이벤트 루프에서 실행되는 함수. 외부에서 메시지 큐에 넣어준 명령을 수행한다.
        """
        self.logger.info("start _listen_message_queue")
        while not self.stop_event.is_set():
            if not self.message_queue.empty():
                message = self.message_queue.get()
                if message == "stop":
                    await self.stop()
                    return

            await asyncio.sleep(1)
        self.logger.info("end _listen_message_queue")

    def on_pending_order_update(
        self,
        status,
        event: OrderEvent,
    ):
        self.event_snapshot_queue.put(self._make_event_snapshot(status, event))

    def _make_event_snapshot(self, status, event: OrderEvent):
        """
        OrderEvent를 이벤트 스냅샷으로 변환합니다
        """

        return {
            "account_info": self.simple_api.get_account(),
            "pending_orders": self.tracker.pending_orders,
            "positions": self.tracker.positions,
            "status": status,
            "event": event,
        }


def run_subprocess(fee_rate, event_snapshot_queue, message_queue, auth_info=None):
    """
    args
    event_snapshot_queue: multiprocessing.Queue[Dict]
        거래 이벤트와 그 상태의 position, order, 계좌정보가 담겨있는 딕셔너리
    message_queue: multiprocessing.Queue[String]
        TradingTrackerMultiProcessWorker를 제어하는데 사용되는 메시지 큐

    """

    print("run_subprocess called")
    worker = TradingTrackerMultiProcessWorker(fee_rate=fee_rate, event_snapshot_queue=event_snapshot_queue, message_queue=message_queue, auth_info=auth_info)
    asyncio.run(worker.start())
