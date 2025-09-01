from pyqqq.brokerage.ebest.oauth import EBestAuth
from pyqqq.brokerage.ebest.simple import EBestSimpleDomesticStock
from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.brokerage.kis.simple import KISSimpleDomesticStock
from pyqqq.brokerage.tracker import TradingTracker
from pyqqq.utils.market_schedule import get_market_schedule
from pyqqq.utils.logger import get_logger
from pyqqq.datatypes import OrderSide, OrderType
from typing import Dict, List, Tuple
import asyncio
import datetime as dtm
import numpy as np
import os
import traceback
import dotenv

logger = get_logger(__name__)


class HookExecutor:

    def __init__(self, strategy_module, interval: dtm.timedelta = dtm.timedelta(seconds=60)):
        self.strategy_module = strategy_module
        self.brokerage = None
        self.stock_broker = None
        self.app_key = None
        self.app_secret = None
        self.account_number = None
        self.account_product_code = None
        self.hts_id = None
        self.tracker = None
        self.paper_trading = False
        self.broker_settings = {}
        self.current_ts = 0
        self.stock_broker_factory = None
        self.market_schedule_factory = None
        self.time_factory = None
        self.keep_alive = lambda: True
        self.adjusting_start_time = False

        self.interval = interval  # 전략 호출 주기
        self.stop_loss_config = {}  # 손절 조건 설정
        self.take_profit_config = {}  # 익절 조건 설정
        self.market_open_time_margin = dtm.timedelta(minutes=5)  # 개장 시간과 거래 시간 사이의 여유 시간
        self.market_close_time_margin = dtm.timedelta(minutes=5)  # 폐장 시간과 거래 시간 사이의 여유 시간
        self.before_market_open_schedule = dtm.timedelta(hours=1)  # 개장 전에 호출되는 hook이 호출되는 시간
        self.after_market_close_schedule = dtm.timedelta(hours=1)  # 폐장 후에 호출되는 hook이 호출되는 시간

    async def initialize(self):
        self._load_env()

        if self._has_hook("on_initialize"):
            logger.info("[EXECUTOR] Call on_initialize hook")
            user_config = await maybe_awaitable(self.strategy_module.on_initialize())
            self._update_config(user_config)

        if self.brokerage == "kis":
            assert self.app_key is not None, "KIS_APP_KEY is required"
            assert self.app_secret is not None, "KIS_APP_SECRET is required"
            assert self.account_number is not None, "KIS_CANO is required"
            assert self.account_product_code is not None, "KIS_ACNT_PRDT_CD is required"
        else:
            assert self.app_key is not None, "EBEST_APP_KEY is required"
            assert self.app_secret is not None, "EBEST_APP_SECRET is required"

        self.stock_broker = self.create_stock_broker()
        await self.start_trading_tracker()

    def now(self) -> dtm.datetime:
        if self.time_factory is None:
            return dtm.datetime.now()
        else:
            return self.time_factory()

    def today(self) -> dtm.date:
        return self.now().date()

    def create_stock_broker(self):
        if self.stock_broker_factory is None:
            if self.brokerage == "kis":
                auth = KISAuth(self.app_key, self.app_secret, self.paper_trading)
                return KISSimpleDomesticStock(auth, self.account_number, self.account_product_code, self.hts_id)
            elif self.brokerage == "ebest":
                auth = EBestAuth(self.app_key, self.app_secret, self.paper_trading)
                return EBestSimpleDomesticStock(auth)
        else:
            args = {
                "brokerage": self.brokerage,
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "account_number": self.account_number,
                "account_product_code": self.account_product_code,
                "paper_trading": self.paper_trading,
            }
            return self.stock_broker_factory(**args)

    async def start_trading_tracker(self):
        if self.brokerage == "kis" and self.hts_id is None:
            return

        self.tracker = TradingTracker(self.stock_broker)
        await self.tracker.start()

    def _has_hook(self, func_name: str) -> bool:
        """사용자가 구현한 함수가 있는지 확인"""
        return hasattr(self.strategy_module, func_name) and callable(getattr(self.strategy_module, func_name))

    def _load_env(self):
        dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))

        ebest_app_key = os.getenv("EBEST_APP_KEY")
        ebest_app_secret = os.getenv("EBEST_APP_SECRET")
        kis_app_key = os.getenv("KIS_APP_KEY")
        kis_app_secret = os.getenv("KIS_APP_SECRET")

        if all(x is not None for x in [ebest_app_key, ebest_app_secret, kis_app_key, kis_app_secret]):
            raise Exception("Ambiguous brokerage setting. Please set only one of EBEST or KIS")

        self.brokerage = None
        if all(x is not None for x in [ebest_app_key, ebest_app_secret]):
            self.brokerage = "ebest"
        elif all(x is not None for x in [kis_app_key, kis_app_secret]):
            self.brokerage = "kis"
        else:
            raise Exception("Brokerage setting is required. Please set either EBEST or KIS")

        if self.brokerage == "ebest":
            self.app_key = ebest_app_key
            self.app_secret = ebest_app_secret

        elif self.brokerage == "kis":
            self.app_key = kis_app_key
            self.app_secret = kis_app_secret
            self.account_number = os.getenv("KIS_CANO")
            self.account_product_code = os.getenv("KIS_ACNT_PRDT_CD")
            self.hts_id = os.getenv("KIS_HTS_ID")

            assert self.account_number is not None, "KIS_CANO is required"
            assert self.account_product_code is not None, "KIS_ACNT_PRDT_CD is required"

    def _update_config(self, config: Dict) -> None:
        if config is None:
            return

        if not isinstance(config, dict):
            raise Exception("config must be dict type")

        if "paper_trading" in config:
            paper_trading = config.get("paper_trading")
            if type(paper_trading) is not bool:
                raise Exception("paper_trading must be bool")

            self.paper_trading = paper_trading

        if "broker_settings" in config:
            broker_settings = config.get("broker_settings")
            self.broker_settings = broker_settings

        if "interval" in config:
            interval = config.get("interval")
            if type(interval) in [int, float]:
                interval = dtm.timedelta(seconds=interval)
            if not isinstance(interval, dtm.timedelta) or interval.total_seconds() < 10:
                raise Exception("interval must be dtm.timedelta type with at least 10 seconds")
            logger.info(f"Update interval to {interval}")
            self.interval = interval

        if "adjusting_start_time" in config:
            adjusting_start_time = config.get("adjusting_start_time")
            if type(adjusting_start_time) is not bool:
                raise Exception("adjusting_start_time must be bool")

            self.adjusting_start_time = adjusting_start_time

        if "take_profit_config" in config:
            take_profit_config = config.get("take_profit_config")
            if not isinstance(take_profit_config, dict):
                raise Exception("take_profit_config must be dict type")

            for k, v in take_profit_config.items():
                if type(v) not in [int, float]:
                    raise Exception("take_profit_config must be dict type with int or float value")
                if v <= 0:
                    raise Exception("take_profit_config must be dict type with positive value")
                if type(k) is not str:
                    raise Exception("take_profit_config must be dict type with str key")

                self.take_profit_config = take_profit_config

        if "stop_loss_config" in config:
            stop_loss_config = config.get("stop_loss_config")
            if not isinstance(stop_loss_config, dict):
                raise Exception("stop_loss_config must be dict type")

            for k, v in stop_loss_config.items():
                if type(v) not in [int, float]:
                    raise Exception("stop_loss_config must be dict type with int or float value")
                if v >= 0:
                    raise Exception("stop_loss_config must be dict type with negative value")
                if type(k) is not str:
                    raise Exception("stop_loss_config must be dict type with str key")

                self.stop_loss_config = stop_loss_config

        if "open_market_time_margin" in config:
            open_market_time_margin = config.get("open_market_time_margin")
            if isinstance(open_market_time_margin, dtm.timedelta):
                self.market_open_time_margin = open_market_time_margin
            elif type(open_market_time_margin) is int:
                self.market_open_time_margin = dtm.timedelta(seconds=open_market_time_margin)
            else:
                raise Exception("open_market_time_margin must be int or dtm.timedelta type")

        elif "market_open_time" in config:
            market_open_time = config.get("market_open_time")
            if not isinstance(market_open_time, dtm.time):
                raise Exception("market_open_time must be time type")

            tm = dtm.datetime.combine(dtm.date.today(), market_open_time)
            if tm < self.market_open_time:
                raise Exception("market_open_time must be earlier than market open time")

            self.market_open_time_margin = tm - self.market_open_time

        if "close_market_time_margin" in config:
            close_market_time_margin = config.get("close_market_time_margin")
            if isinstance(close_market_time_margin, dtm.timedelta):
                self.market_close_time_margin = close_market_time_margin
            elif type(close_market_time_margin) is int:
                self.market_close_time_margin = dtm.timedelta(seconds=close_market_time_margin)
            else:
                raise Exception("close_market_time_margin must be int or dtm.timedelta type")

        elif "market_close_time" in config:
            market_close_time = config.get("market_close_time")
            if not isinstance(market_close_time, dtm.time):
                raise Exception("market_close_time must be time type")

            tm = dtm.datetime.combine(dtm.date.today(), market_close_time)
            if tm > self.market_close_time:
                raise Exception("market_close_time must be later than market close time")

            self.market_close_time_margin = self.market_close_time - tm

        if "before_market_open_schedule" in config:
            before_market_open_schedule = config.get("before_market_open_schedule")
            if type(before_market_open_schedule) is int:
                self.before_market_open_schedule = dtm.timedelta(seconds=before_market_open_schedule)
            elif isinstance(before_market_open_schedule, dtm.timedelta):
                self.before_market_open_schedule = before_market_open_schedule
            elif isinstance(before_market_open_schedule, dtm.time):
                self.before_market_open_schedule = before_market_open_schedule
            else:
                raise Exception("before_market_open_schedule must be int, dtm.timedelta or time type")

        if "after_market_close_schedule" in config:
            after_market_close_schedule = config.get("after_market_close_schedule")
            if type(after_market_close_schedule) is int:
                self.after_market_close_schedule = dtm.timedelta(seconds=after_market_close_schedule)
            elif isinstance(after_market_close_schedule, dtm.timedelta):
                self.after_market_close_schedule = after_market_close_schedule
            elif isinstance(after_market_close_schedule, dtm.time):
                self.after_market_close_schedule = after_market_close_schedule
            else:
                raise Exception("after_market_close_schedule must be int, dtm.timedelta or time type")

    async def monitor_stop_loss(self, positions: List, stop_loss_config: Dict = {}) -> None:
        logger.info("monitor_stop_loss")

        if self._has_hook("monitor_stop_loss"):
            await maybe_awaitable(
                self.strategy_module.monitor_stop_loss(
                    positions=positions,
                    stop_loss_config=stop_loss_config,
                    broker=self.stock_broker,
                )
            )
        else:
            """
            * 사용자가 구현하지 않은 경우 기본 로직 실행
            """
            for p in positions:
                asset_stop_loss_threshold = stop_loss_config.get(p.asset_code)
                if asset_stop_loss_threshold is not None:
                    # 사용자가 지정한 종목별 stop loss 레벨이 음수가 아닌 경우, 음수로 변환
                    if np.sign(asset_stop_loss_threshold) == 1:
                        asset_stop_loss_threshold *= -1

                    if p.current_pnl <= asset_stop_loss_threshold:
                        self.stock_broker.create_order(p.asset_code, OrderSide.SELL, p.quantity)

    async def monitor_take_profit(self, positions: List, take_profit_config: Dict = {}) -> None:
        logger.info("monitor_take_profit")

        if self._has_hook("monitor_take_profit"):
            return await maybe_awaitable(
                self.strategy_module.monitor_take_profit(
                    positions=positions,
                    take_profit_config=take_profit_config,
                    broker=self.stock_broker,
                )
            )
        else:
            """
            * 사용자가 구현하지 않은 경우 기본 로직 실행
            """
            for p in positions:
                asset_take_profit_threshold = take_profit_config.get(p.asset_code)
                if asset_take_profit_threshold is not None:
                    # 사용자가 지정한 종목별 take profit 레벨을 양수로 변환
                    asset_take_profit_threshold = abs(asset_take_profit_threshold)

                    if p.current_pnl >= asset_take_profit_threshold:
                        self.stock_broker.create_order(p.asset_code, OrderSide.SELL, p.quantity)

    def execute_trades(self, trade_signals: List) -> None:
        """
        매매 지시에 따른 주문 제출
        - 매도 지시 먼저 완료 후 매수 지시 진행
        """
        buy_signals = []
        sell_signals = []

        for signal in trade_signals:
            if signal[2] > 0:
                buy_signals.append(signal)
            else:
                sell_signals.append(signal)

        for ts in sell_signals:
            asset_code = ts[0]
            price = int(ts[1])
            quantity = abs(int(ts[2]))
            side = OrderSide.SELL
            order_type = OrderType.LIMIT if price > 0 else OrderType.MARKET

            self.stock_broker.create_order(
                asset_code,
                side,
                quantity,
                order_type,
                price,
            )

        for ts in buy_signals:
            asset_code = ts[0]
            price = int(ts[1])
            quantity = abs(int(ts[2]))
            side = OrderSide.BUY
            order_type = OrderType.LIMIT if price > 0 else OrderType.MARKET

            self.stock_broker.create_order(
                asset_code,
                side,
                quantity,
                order_type,
                price,
            )

    def is_trading_day(self) -> bool:
        schedule = self.get_market_schedule()

        return not schedule.full_day_closed

    @property
    def market_open_time(self) -> dtm.datetime:
        """오늘 개장 시간"""
        schedule = self.get_market_schedule()

        if schedule.open_time:
            open_time = schedule.open_time
        else:
            open_time = dtm.time(9, 0)

        return dtm.datetime.combine(self.today(), open_time)

    @property
    def market_close_time(self) -> dtm.datetime:
        """오늘 폐장 시간 (동시호가 시작)"""

        schedule = self.get_market_schedule()

        if schedule.close_time:
            close_time = schedule.close_time
        else:
            close_time = dtm.time(15, 30)

        return dtm.datetime.combine(self.today(), close_time) - dtm.timedelta(minutes=10)

    def get_market_schedule(self):
        if self.market_schedule_factory is None:
            return get_market_schedule(self.today())
        else:
            return self.market_schedule_factory()

    @property
    def user_defined_market_open_time(self) -> dtm.datetime:
        """사용자가 설정한 여유 시간 간격을 반영한 개장 시간"""
        return self.market_open_time + self.market_open_time_margin

    @property
    def market_open_callback_threshold(self) -> dtm.datetime:
        """이 시간 이내에 앱이 실행 중이어야 개장 시간에 대한 콜백을 호출함

        기본값은 사용자 정의 개장 시간으로부터 5분 이내.
        그 이후에 전략이 시작 된 경우에는 on_market_open 콜백이 호출하지 않음.
        """
        return self.user_defined_market_open_time + dtm.timedelta(minutes=5)

    @property
    def user_defined_market_close_time(self) -> dtm.datetime:
        """사용자가 설정한 여유 시간 간격을 반영한 폐장 시간"""
        return self.market_close_time - self.market_close_time_margin

    @property
    def before_market_open_hook_call_time(self) -> dtm.datetime:
        """개장 전에 호출되는 hook이 호출되는 시간"""
        if isinstance(self.before_market_open_schedule, dtm.time):
            return dtm.datetime.combine(self.today(), self.before_market_open_schedule)
        else:
            return self.user_defined_market_open_time - self.before_market_open_schedule

    @property
    def before_market_open_hook_call_time_threshold(self) -> dtm.datetime:
        """개장 전에 호출되는 hook이 호출되는 시간에 대한 threshold

        기본값은 개장 전에 5분 이내에 앱이 실행 중이어야 개장 전 콜백을 호출함
        """
        return self.before_market_open_hook_call_time + dtm.timedelta(minutes=5)

    @property
    def after_market_close_hook_call_time(self) -> dtm.datetime:
        """폐장 후에 호출되는 hook이 호출되는 시간"""
        if isinstance(self.after_market_close_schedule, dtm.time):
            return dtm.datetime.combine(self.today(), self.after_market_close_schedule)
        else:
            return self.user_defined_market_close_time + self.after_market_close_schedule

    @property
    def after_market_close_hook_call_time_threshold(self) -> dtm.datetime:
        """폐장 후에 호출되는 hook이 호출되는 시간에 대한 threshold

        기본값은 폐장 후에 5분 이내에 앱이 실행 중이어야 폐장 후 콜백을 호출함
        """
        return self.after_market_close_hook_call_time + dtm.timedelta(minutes=5)

    def is_trading_time(self) -> bool:
        schedule = self.get_market_schedule()

        if schedule.full_day_closed:
            return False

        now = self.now()

        open_time = min(self.market_open_time, self.user_defined_market_open_time)

        if now < open_time:
            return False

        if now > self.market_close_time:
            return False

        return True

    async def run(self):
        await self.initialize()
        await self._run_intraday_strategy()

        if self.tracker is not None:
            await self.tracker.stop()
            await asyncio.gather(self.tracker.task, return_exceptions=True)

    async def _run_intraday_strategy(self):
        market_close_inform_interval = dtm.timedelta(minutes=5)

        today = dtm.datetime.fromtimestamp(0).date()
        last_call_time = dtm.datetime.fromtimestamp(0)
        last_market_close_inform_time = dtm.datetime.fromtimestamp(0)

        market_opened = False
        market_closed = False
        before_market_open_hook_called = False
        after_market_close_hook_called = False

        if self.adjusting_start_time:
            await self._sleep_until_next_interval()

        while True:
            now = self.now()
            self.current_ts = int(now.timestamp() * 1000)

            if now.date() != today:
                today = now.date()
                market_opened = False
                market_closed = False
                before_market_open_hook_called = False
                after_market_close_hook_called = False
                last_call_time = dtm.datetime.fromtimestamp(0)
                last_market_close_inform_time = dtm.datetime.fromtimestamp(0)

                logger.info(f"New day. {today.strftime('%Y-%m-%d')}")
                logger.info(f"-  before_open_call_time: {self.before_market_open_hook_call_time.strftime('%H:%M:%S')}")
                logger.info(f"-       market_open_time: {self.market_open_time.strftime('%H:%M:%S')}")
                logger.info(f"-  user_market_open_time: {self.user_defined_market_open_time.strftime('%H:%M:%S')}")
                logger.info(f"- user_market_close_time: {self.user_defined_market_close_time.strftime('%H:%M:%S')}")
                logger.info(f"-      market_close_time: {self.market_close_time.strftime('%H:%M:%S')}")
                logger.info(f"-  after_close_call_time: {self.after_market_close_hook_call_time.strftime('%H:%M:%S')}")
                logger.info(f"-               interval: {self.interval.seconds} seconds")
                logger.info(f"-           start_margin: {int(self.market_open_time_margin.total_seconds())} seconds")
                logger.info(f"-             end_margin: {int(self.market_close_time_margin.total_seconds())} seconds")
                logger.info(f"               brokerage: {self.brokerage}")
                logger.info(f"           paper_trading: {self.paper_trading}")
                logger.info("")

            try:
                if self.is_trading_time():
                    if not market_opened and now >= self.user_defined_market_open_time:
                        market_opened = True

                        # 시작이 시작되고, market_open_callback_threshold 시간이 지나지 않은 경우 콜백 함수 호출
                        if now <= self.market_open_callback_threshold:
                            last_call_time = now
                            await self.on_market_open()

                    # 장 종료시 최종 1회 실행되는 함수 호출
                    elif not market_closed and now >= self.user_defined_market_close_time:
                        market_closed = True

                        if now < self.market_close_time:
                            last_call_time = now
                            await self.on_market_close()

                    # 장 시작 후 사용자 설정 주기마다 전략 실행
                    elif market_opened and not market_closed and now >= (last_call_time + self.interval):
                        last_call_time = now
                        await self.trade()
                else:
                    if now >= (last_market_close_inform_time + market_close_inform_interval):
                        last_market_close_inform_time = now
                        logger.info("[EXECUTOR] Not trading time.")

                if self.is_trading_day():
                    if not before_market_open_hook_called and now >= self.before_market_open_hook_call_time:
                        before_market_open_hook_called = True
                        if now <= self.before_market_open_hook_call_time_threshold:
                            await self.on_before_market_open()

                    if not after_market_close_hook_called and now >= self.after_market_close_hook_call_time:
                        after_market_close_hook_called = True
                        if now <= self.after_market_close_hook_call_time_threshold:
                            await self.on_after_market_close()

            except KeyboardInterrupt:
                logger.info("Got keyboard interrupt. stop loop")
                break
            except asyncio.CancelledError:
                logger.info("Got cancelled error. stop loop")
                break
            except Exception:
                traceback.print_exc()

            if not self.keep_alive():
                break

            await asyncio.sleep(1.0 - (dtm.datetime.now().time().microsecond / 1000000))

    async def _sleep_until_next_interval(self):
        """다음 interval에 맞춰 sleep"""
        current_seq = self._calc_clock_seq(interval=self.interval)
        next_seq_time = self._get_time_of_seq(current_seq + 1, self.interval)
        sleep_seconds = (next_seq_time - self.now()).total_seconds()

        logger.info(f"Sleep to adjust to next interval: {sleep_seconds} seconds")
        await asyncio.sleep(sleep_seconds)

    def _get_time_of_seq(self, seq: int, interval=dtm.timedelta(seconds=60)) -> dtm.datetime:
        """시퀀스 번호를 시간으로 변환"""
        return self.market_open_time + seq * interval

    def _calc_clock_seq(
        self,
        interval=dtm.timedelta(seconds=60),
        t: dtm.datetime = None,
    ):
        """현재 시각을 기준으로 시간대별 시퀀스 번호를 계산합니다"""
        open_time = self.market_open_time
        clock_time = dtm.datetime.now() if t is None else t
        elapsed = clock_time - open_time
        return int(elapsed.total_seconds() / interval.total_seconds())

    async def trade(self) -> None:
        """
        일정 주기마다 전반적인 트레이딩 시스템을 실행

        Steps:
        1. get pending orders
        2. handle pending orders
        3. get positions
        4. monitor stop loss
        5. monitor take profit
        6. get available cash
        7. generate signals from strategy (custom)
        8. execute trades

        NOTE 전략이 실행되는 시간이 길어질 수 있음. 다음 실행 시간은 전략 실행 종료에 따라 설정되어야 할 것.
        """

        # 미체결 주문 관리
        pending_orders = self.stock_broker.get_pending_orders()
        await self.handle_pending_orders(pending_orders=pending_orders)

        # 보유 포지션 조회
        positions = self.stock_broker.get_positions()

        if len(positions) > 0 and (len(self.stop_loss_config) > 0 or len(self.take_profit_config) > 0):
            # Stop loss 및 take profit 주문 집행
            await self.monitor_stop_loss(positions=positions, stop_loss_config=self.stop_loss_config)
            await self.monitor_take_profit(positions=positions, take_profit_config=self.take_profit_config)

            # 보유 포지션 조회 (최신 상태로 갱신)
            positions = self.stock_broker.get_positions()

        # 전략에 의한 매매 지시 획득
        account_info = self.stock_broker.get_account()
        pending_orders = self.stock_broker.get_pending_orders()

        # 사용자 전략 로직
        trade_signals = await self.trade_func(account_info, pending_orders, positions)

        # 매매 지시에 의한 주문 집행
        self.execute_trades(trade_signals=trade_signals)

    # ----------------------------------------------------------------------------------------------------
    # 사용자 설정 가능한 함수
    # ----------------------------------------------------------------------------------------------------

    def validate_trade_signal(self, trade_signals: List[Tuple[str, int, int]], tag: str = "hook"):
        if trade_signals is None:
            return []

        assert isinstance(trade_signals, list), f"{tag} must return list type"

        for r in trade_signals:
            assert isinstance(r, tuple), f"{tag} must return list of tuple"
            assert len(r) == 3, f"{tag} must return list of tuple with 3 elements"
            assert type(r[0]) is str, f"{tag} must return list of tuple with str type as first element(asset_code)"
            assert type(r[1]) is int, f"{tag} must return list of tuple with int type as second element(price)"
            assert type(r[2]) is int, f"{tag} must return list of tuple with int type as third element(quantity)"
            assert r[2] != 0, f"{tag} must return list of tuple with non-zero int value as third element(quantity)"

        return trade_signals

    def handle_pending_orders_executor(self, trade_instructions: List):
        """
        handle_pending_orders에서 반환되는 trade_instructions:
        trade_instructions = [
                                (asset_code, order_id, price, quantity),
                             ]

        잔량/일부 취소만 가능 => 취소 지시는 가격은 None으로 지정하고, 최대 "잔량"과 같거나 적은 수량(0 이상이여야 함)을 입력하면 처리 됨
        - 수량은 음수 (int)
        - 취소 지시는 가격을 입력해도 무시됨 (음수 수량 instruction은 취소주문 전용)


        정정은 보유수량 최대까지만 정정 가능 (그 이상은 추가 매수이기 때문에 정정 처리가 안됨)
        - 가격은 필수 (int)
        - 수량은 양수 (int)


        *예시*
        보유 포지션: A005930, 5000원, 100주

        [취소]
        부분 취소: 100주에서 50주로 수량 정정 (부분 취소와 수량 정정이 동일함) => (A005930, None, -50)
        전량 취소: 100주에서 0주로 수량 정정 (전량 취소) => (A005930, None, -100)

        [정정]
        - 100주를 4800원으로 정정 => (A005930, 4800, 100)
        - 50주를 4900원으로 정정 (나머지 50주는 5000원에 유지) => (A005930, 4900, 50)


        """
        for instruction in trade_instructions:
            if len(instruction) != 4:
                raise Exception("trade_instructions must be list of tuple with 4 elements")

            code = instruction[0]
            order_id = instruction[1]
            price = instruction[2]
            quantity = instruction[3]

            if not isinstance(code, str):
                raise TypeError("Asset Code must be a string.")
            if not isinstance(quantity, int):
                raise TypeError("Quantity must be an integer.")

            if quantity < 0:
                # 취소 주문. quantity만큼 취소 주문 제출
                if self.brokerage == "kis":
                    self.stock_broker.cancel_order(order_id, abs(quantity))
                else:
                    self.stock_broker.cancel_order(order_id, code, abs(quantity))

            elif quantity > 0:
                if not isinstance(price, int):
                    raise TypeError("Price must be an integer.")

                # 정정 주문. quantity를 price에 정정 주문 제출
                if self.brokerage == "kis":
                    self.stock_broker.update_order(order_id, OrderType.LIMIT, price, quantity)
                else:
                    self.stock_broker.update_order(order_id, code, OrderType.LIMIT, price, quantity)

    async def handle_pending_orders(self, pending_orders: List[Tuple[str, List]]) -> None:
        """
        미체결 주문 처리 방식
        - 디폴트 설정은 취소 주문을 접수하도록 구현

        * 사용자가 override할 수 있도록 구현
        """
        if self._has_hook("handle_pending_orders"):
            logger.info("[EXECUTOR] Call handle_pending_orders hook")
            trade_instructions = await maybe_awaitable(self.strategy_module.handle_pending_orders(pending_orders, self.stock_broker))
            if isinstance(trade_instructions, list) and len(trade_instructions) > 0:
                self.handle_pending_orders_executor(trade_instructions)
        else:
            for orders in pending_orders:
                for po in orders:
                    if self.brokerage == "kis":
                        self.stock_broker.cancel_order(po.order_no, po.pending_quantity)
                    else:
                        self.stock_broker.cancel_order(
                            po.order_no,
                            po.asset_code,
                            po.pending_quantity,
                        )

    async def on_market_open(self):
        """
        장 시작 시 최초에 1회 실행되는 함수
        사용자가 설정하는 전략 함수
        """
        if self._has_hook("on_market_open"):
            account_info = self.stock_broker.get_account()
            positions = self.stock_broker.get_positions()
            pending_orders = self.stock_broker.get_pending_orders()

            logger.info("[EXECUTOR] Call on_market_open hook")
            trade_signals = await maybe_awaitable(
                self.strategy_module.on_market_open(
                    account_info,
                    pending_orders,
                    positions,
                    self.stock_broker,
                )
            )

            if isinstance(trade_signals, list) and len(trade_signals) > 0:
                self.validate_trade_signal(trade_signals, tag="on_market_open")
                self.execute_trades(trade_signals=trade_signals)

    async def trade_func(self, account_info: Dict, pending_orders: List, positions: List) -> List[Tuple[str, int]]:
        """
        장 중에 연속적으로 실행되는 함수
        사용자가 설정하는 전략 함수

        :return List[Tuple[str, int, int]]: 종목코드, 주문 가격, 주문 수량을 반환하여 매매 지시
        """
        if self._has_hook("trade_func"):
            logger.info("[EXECUTOR] Call trade_func hook")
            result = await maybe_awaitable(self.strategy_module.trade_func(account_info, pending_orders, positions, self.stock_broker))
            if result is None:
                return []

            self.validate_trade_signal(result, tag="trade_func")
            return result
        else:
            return []

    async def on_market_close(self):
        """
        장 마감 시 최종적으로 1회 실행되는 함수
        사용자가 설정하는 전략 함수
        """
        if self._has_hook("on_market_close"):
            account_info = self.stock_broker.get_account()
            positions = self.stock_broker.get_positions()
            pending_orders = self.stock_broker.get_pending_orders()

            logger.info("[EXECUTOR] Call on_market_close hook")
            trade_signals = await maybe_awaitable(
                self.strategy_module.on_market_close(
                    account_info,
                    pending_orders,
                    positions,
                    self.stock_broker,
                )
            )

            if isinstance(trade_signals, list) and len(trade_signals) > 0:
                self.validate_trade_signal(trade_signals, tag="on_market_close")
                self.execute_trades(trade_signals=trade_signals)

    async def on_before_market_open(self):
        """매일 장 시작 전 1회 실행되는 함수"""
        if self._has_hook("on_before_market_open"):
            account_info = self.stock_broker.get_account()
            positions = self.stock_broker.get_positions()
            pending_orders = self.stock_broker.get_pending_orders()

            logger.info("[EXECUTOR] Call on_before_market_open hook")
            await maybe_awaitable(
                self.strategy_module.on_before_market_open(
                    account_info=account_info,
                    pending_orders=pending_orders,
                    positions=positions,
                    broker=self.stock_broker,
                )
            )

    async def on_after_market_close(self):
        """매일 장 종료 후 1회 실행되는 함수"""
        if self._has_hook("on_after_market_close"):
            account_info = self.stock_broker.get_account()
            positions = self.stock_broker.get_positions()
            pending_orders = self.stock_broker.get_pending_orders()

            logger.info("[EXECUTOR] Call on_after_market_close hook")
            await maybe_awaitable(
                self.strategy_module.on_after_market_close(
                    account_info=account_info,
                    pending_orders=pending_orders,
                    positions=positions,
                    broker=self.stock_broker,
                )
            )


async def maybe_awaitable(result):
    if asyncio.iscoroutine(result) or isinstance(result, asyncio.Future):
        return await result
    else:
        return result
