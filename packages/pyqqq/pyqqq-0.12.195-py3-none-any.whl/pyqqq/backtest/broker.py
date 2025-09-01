import datetime as dtm
import os
import fcntl
from abc import ABC, abstractmethod
from dataclasses import asdict
from decimal import Decimal
from functools import lru_cache
from typing import List, Literal, Optional, Union

import numpy as np
import pandas as pd

from pyqqq.backtest.logger import Logger, get_logger
from pyqqq.backtest.positionprovider import BasePositionProvider
from pyqqq.backtest.wallclock import WallClock
from pyqqq.brokerage.kis.simple import KISSimpleDomesticStock
from pyqqq.brokerage.kis.simple_overseas import KISSimpleOverseasStock
from pyqqq.data.daily import get_ohlcv_by_codes_for_period as get_kr_daily_data
from pyqqq.data.domestic import get_market_cap_by_codes
from pyqqq.data.domestic import get_ticker_info as get_kr_ticker_info
from pyqqq.data.minutes import get_all_day_data as get_kr_minute_data
from pyqqq.data.us_stocks import get_all_day_data as get_us_minute_data
from pyqqq.data.us_stocks import get_ohlcv_by_codes_for_period as get_us_daily_data
from pyqqq.data.us_stocks import get_ticker_info as get_us_ticker_info
from pyqqq.datatypes import *
from pyqqq.utils.casting import casting
from pyqqq.utils.market_schedule import get_last_trading_day, get_market_schedule, get_trading_day_with_offset
from pyqqq.utils.position_classifier import PositionClassifier

MarketType = Literal["kr_stock", "us_stock"]


class BaseBroker(ABC):
    """브로커 인터페이스를 구현하기 위한 기본 클래스입니다.

    이 클래스는 모든 브로커 구현체가 따라야 하는 표준 인터페이스를 정의합니다.
    계좌 관리, 시장 데이터 조회, 주문 실행을 위한 메서드들을 제공합니다.
    구체적인 구현체는 모든 메서드를 오버라이드해야 합니다.

    Attributes:
        없음

    Note:
        이 클래스는 추상 기본 클래스이므로 직접 인스턴스화해서는 안 됩니다.
        모든 메서드는 NotImplementedError를 발생시키며 구체적인 하위 클래스에서 구현되어야 합니다.
    """

    @abstractmethod
    def get_account(self) -> dict:
        """현재 계좌 정보를 조회합니다.

        Returns:
            dict: 다음 정보를 포함하는 계좌 정보:
                - total_balance (int|Decimal): 총 평가 금액
                - purchase_amount (int|Decimal): 매입 금액
                - evaluated_amount (int|Decimal): 평가 금액
                - pnl_amount (int|Decimal): 손익 금액
                - pnl_rate (Decimal): 손익률

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
        """
        raise NotImplementedError

    @abstractmethod
    def get_price(self, code: str) -> Decimal:
        """특정 종목의 현재 가격을 조회합니다.

        Args:
            code (str): 가격을 조회할 종목 코드

        Returns:
            Decimal: 해당 종목의 현재 가격

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
        """
        raise NotImplementedError

    @abstractmethod
    def get_minute_price(self, code: str) -> pd.DataFrame:
        """특정 종목의 분단위 가격 데이터를 조회합니다.

        Args:
            code (str): 가격 데이터를 조회할 종목 코드

        Returns:
            pd.DataFrame: 다음 열을 포함하는 분단위 가격 데이터:
                - time (datetime): 시간
                - open (Decimal): 시가
                - high (Decimal): 고가
                - low (Decimal): 저가
                - close (Decimal): 종가
                - volume (int): 거래량

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
        """
        raise NotImplementedError

    @abstractmethod
    def get_daily_price(self, code: str, from_date: dtm.date, to_date: dtm.date) -> pd.DataFrame:
        """특정 기간 동안의 일별 가격 데이터를 조회합니다.

        Args:
            code (str): 가격 데이터를 조회할 종목 코드
            from_date (datetime.date): 조회 시작일 (포함)
            to_date (datetime.date): 조회 종료일 (포함)

        Returns:
            pd.DataFrame: 다음 열을 포함하는 일별 가격 데이터:
                - date (datetime): 거래일
                - open (Decimal): 시가
                - high (Decimal): 고가
                - low (Decimal): 저가
                - close (Decimal): 종가
                - volume (int): 거래량

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
        """
        raise NotImplementedError

    @abstractmethod
    def get_pending_orders(
        self,
        exchanges: List[OrderExchange] = [OrderExchange.KRX]
    ) -> List[StockOrder]:
        """미체결된 모든 주문을 조회합니다.
        Args:
            exchanges (List[OrderExchange], optional): 조회할 거래소 리스트 (기본값: [OrderExchange.KRX])
        Returns:
            List[StockOrder]: 미체결 주문 객체 리스트

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
        """
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> List[StockPosition]:
        """모든 종목의 현재 포지션을 조회합니다.

        Returns:
            List[StockPosition]: 현재 보유 중인 포지션을 나타내는 객체 리스트

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
        """
        raise NotImplementedError

    @abstractmethod
    def create_order(self, asset_code: str, side: OrderSide, quantity: int, order_type: OrderType = OrderType.MARKET, price: int | Decimal = 0, exchange: OrderExchange = OrderExchange.KRX) -> str:
        """새로운 주문을 생성합니다.

        Args:
            asset_code (str): 주문할 종목 코드
            side (OrderSide): 매수/매도 구분
            quantity (int): 주문 수량
            order_type (OrderType, optional): 주문 타입 (기본값: MARKET)
            price (int, optional): 지정가 주문 시 주문 가격 (기본값: 0)
            exchange (OrderExchange, optional): 거래소 (기본값: KRX)

        Returns:
            str: 생성된 주문 번호

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
            ValueError: 잘못된 주문 정보가 제공된 경우
        """
        raise NotImplementedError

    @abstractmethod
    def update_order(self, org_order_no: str, order_type: OrderType, price: int | Decimal, quantity: int = 0, exchange: OrderExchange = OrderExchange.KRX) -> str:
        """기존 주문을 수정합니다.

        Args:
            org_order_no (str): 원래 주문 번호
            order_type (OrderType): 변경할 주문 타입
            price (int): 변경할 주문 가격
            quantity (int, optional): 변경할 주문 수량 (기본값: 0, 전량)

        Returns:
            str: 새로 생성된 주문 번호

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
            ValueError: 잘못된 주문 정보가 제공된 경우
            Exception: 원래 주문을 찾을 수 없는 경우
        """
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_no: str, quantity: int = 0) -> str:
        """주문을 취소합니다.

        Args:
            order_no (str): 취소할 주문 번호
            quantity (int, optional): 취소할 수량 (기본값: 0, 전량 취소)

        Raises:
            NotImplementedError: 이 메서드는 구체적인 하위 클래스에서 구현되어야 합니다.
            Exception: 취소할 주문을 찾을 수 없는 경우
        """
        raise NotImplementedError


# 모의 계좌나 실제 계좌로 트레이딩 할때 사용되는 브로커
class TradingBroker(BaseBroker):
    """실제 거래를 수행하는 브로커 클래스입니다.

    이 클래스는 실제 계좌나 모의 계좌를 통해 주식 거래를 수행합니다.
    데이터 조회용 API와 거래용 API를 분리하여 관리하며,
    KIS (한국투자증권)의 국내주식과 해외주식 API를 지원합니다.

    Note:
        - data_api와 trading_api는 서로 다른 인스턴스일 수 있으며,
          이를 통해 시세 조회와 거래를 분리하여 처리할 수 있습니다.
        - KIS의 국내주식과 해외주식 API를 모두 지원하므로,
          필요에 따라 적절한 API를 선택하여 사용할 수 있습니다.
        - 모든 거래 관련 작업은 로그로 기록되며, logging 레벨은 DEBUG로 설정됩니다.

    Example:

    .. highlight:: python
    .. code-block:: python

        # 국내주식 거래의 경우
        data_api = KISSimpleDomesticStock(...)
        trading_api = KISSimpleDomesticStock(...)
        broker = TradingBroker(data_api, trading_api)

        # 해외주식 거래의 경우
        data_api = KISSimpleOverseasStock(...)
        trading_api = KISSimpleOverseasStock(...)
        broker = TradingBroker(data_api, trading_api)

    """

    data_api: Union[KISSimpleDomesticStock, KISSimpleOverseasStock]
    """ 시세 조회 및 시장 데이터 조회를 위한 API 인터페이스 """
    trading_api: Union[KISSimpleDomesticStock, KISSimpleOverseasStock]
    """ 실제 주문 및 거래 실행을 위한 API 인터페이스 """
    logger: Logger
    """ 로깅을 위한 logger 인스턴스 """

    def __init__(
        self,
        data_api: Union[KISSimpleDomesticStock, KISSimpleOverseasStock],
        trading_api: Union[KISSimpleDomesticStock, KISSimpleOverseasStock],
        clock: WallClock,
        market_nxt_on: bool = False,
        strategy_name: Optional[str] = None,
        classifier_type: Optional[str] = None,
    ):
        """TradingBroker 클래스의 초기화 메서드입니다.

        Args:
            data_api (Union[KISSimpleDomesticStock, KISSimpleOverseasStock]):
                시세 조회 및 시장 데이터 조회를 위한 API 인터페이스
            trading_api (Union[KISSimpleDomesticStock, KISSimpleOverseasStock]):
                실제 주문 및 거래 실행을 위한 API 인터페이스

        Note:
            생성된 인스턴스는 즉시 거래가 가능한 상태가 되며,
            모든 거래 관련 작업은 자동으로 로깅됩니다.
        """
        self.logger = get_logger("TradingBroker", clock)
        self.data_api = data_api
        self.trading_api = trading_api
        self.market_nxt_on = market_nxt_on
        self.position_classifier = None

        if classifier_type and classifier_type in ["auto", "direct"]:
            if strategy_name:
                kv_store_collection = f"{strategy_name}_classifier"
            else:
                kv_store_collection = f"account_{self.trading_api.account_no}_classifier"
            self.position_classifier = PositionClassifier(simple_data_api=self.trading_api, kv_store_collection=kv_store_collection, default_type=classifier_type)

    def get_account(self) -> dict:
        return self.trading_api.get_account()

    def get_price(self, code: str, data_exchange: Optional[DataExchange] = None) -> Decimal:
        if data_exchange:
            price_data = self.data_api.get_price(code, data_exchange=data_exchange)
            if data_exchange == DataExchange.NXT and price_data.get("open_price", 0) == 0:  # current_price는 어제의 값을 반환하므로 open_price가 0인지로 NXT 시장 여부 확인
                price_data = self.data_api.get_price(code, data_exchange=DataExchange.KRX)
        else:
            if self.market_nxt_on:
                price_data = self.data_api.get_price(code, data_exchange=DataExchange.UN)
                if price_data.get("open_price", 0) == 0:  # current_price는 어제의 값을 반환하므로 open_price가 0인지로 NXT 시장 여부 확인
                    price_data = self.data_api.get_price(code, data_exchange=DataExchange.KRX)
            else:
                price_data = self.data_api.get_price(code, data_exchange=DataExchange.KRX)

        result = price_data.get("current_price")
        if result is None:
            raise ValueError(f"Current price not found: {code}")
        return Decimal(str(result))

    def get_minute_price(self, code: str, data_exchange: Optional[DataExchange] = None) -> pd.DataFrame:
        if data_exchange:
            result = self.data_api.get_today_minute_data(code, data_exchange=data_exchange)
            if data_exchange == DataExchange.NXT and (result.empty or result.iloc[-1].close == 0):
                result = self.data_api.get_today_minute_data(code, data_exchange=DataExchange.KRX)
        else:
            if self.market_nxt_on:
                result = self.data_api.get_today_minute_data(code, data_exchange=DataExchange.UN)
                if result.empty or result.iloc[-1].close == 0:
                    result = self.data_api.get_today_minute_data(code, data_exchange=DataExchange.KRX)
            else:
                result = self.data_api.get_today_minute_data(code, data_exchange=DataExchange.KRX)
        return result

    def get_daily_price(self, code: str, from_date: dtm.date, to_date: dtm.date, data_exchange: Optional[DataExchange] = None) -> pd.DataFrame:
        if data_exchange:
            result = self.data_api.get_historical_daily_data(code, from_date, to_date, adjusted_price=True, data_exchange=data_exchange)
            if data_exchange == DataExchange.NXT and (result.empty or result.iloc[0].open == 0):
                result = self.data_api.get_historical_daily_data(code, from_date, to_date, adjusted_price=True, data_exchange=DataExchange.KRX)
        else:
            if self.market_nxt_on:
                result = self.data_api.get_historical_daily_data(code, from_date, to_date, adjusted_price=True, data_exchange=DataExchange.UN)
                if result.empty or result.iloc[0].open == 0:
                    result = self.data_api.get_historical_daily_data(code, from_date, to_date, adjusted_price=True, data_exchange=DataExchange.KRX)
            else:
                result = self.data_api.get_historical_daily_data(code, from_date, to_date, adjusted_price=True, data_exchange=DataExchange.KRX)
        result = result.sort_index(ascending=True)
        return result

    def get_orderbook(self, code: str, data_exchange: Optional[DataExchange] = None):
        if data_exchange:
            result = self.data_api.get_orderbook(code, data_exchange=data_exchange)
            if data_exchange == DataExchange.NXT and not result:
                result = self.data_api.get_orderbook(code, data_exchange=DataExchange.KRX)
        else:
            if self.market_nxt_on:
                result = self.data_api.get_orderbook(code, data_exchange=DataExchange.NXT)
                if not result:
                    result = self.data_api.get_orderbook(code, data_exchange=DataExchange.KRX)
            else:
                result = self.data_api.get_orderbook(code, data_exchange=DataExchange.KRX)
        return result

    def get_pending_orders(self, exchanges: List[OrderExchange] = [OrderExchange.KRX]):
        return self.trading_api.get_pending_orders(exchanges)

    def _get_pending_order(
        self,
        order_no: str,
        exchanges: List[OrderExchange] = [OrderExchange.KRX],
    ) -> StockOrder | None:
        orders = self.get_pending_orders(exchanges=exchanges)
        return next((o for o in orders if o.order_no == order_no), None)

    def get_positions(self):
        """
        포지션 조회 (NXT 가격 반영됨)
        """
        return self.trading_api.get_positions()

    def create_order(self, asset_code: str, side: OrderSide, quantity: int, order_type: OrderType = OrderType.MARKET, price: int | Decimal = 0, exchange: OrderExchange = OrderExchange.KRX) -> str:
        self.logger.debug(f"create_order: {asset_code} {side} {quantity} {order_type} {price} {exchange}")

        if side is OrderSide.SELL and self.position_classifier:
            # 포지션 분류기를 사용하여 전략에서 보유중인 수량으로 매도 가능 수량 재 계산
            calc_quantity = self.position_classifier.get_sellable_quantity(asset_code, quantity)

            if calc_quantity != quantity:
                self.logger.warning(f"Requested sell quantity {quantity} for {asset_code} adjusted to {calc_quantity} based on position classifier.")
                quantity = calc_quantity

        order_no = self.trading_api.create_order(asset_code, side, quantity, order_type, price, exchange=exchange)
        if order_no and self.position_classifier:
            # 주문이 성공적으로 생성되면 포지션 분류기에 주문 정보를 업데이트
            self.position_classifier.tagging_order_auto(order_no)
        return order_no

    def update_order(self, org_order_no: str, order_type: OrderType, price: int | Decimal, quantity: int = 0, exchange: OrderExchange = OrderExchange.KRX):
        if isinstance(self.trading_api, KISSimpleOverseasStock):
            order = self._get_pending_order(org_order_no)
            if order is not None:
                self.logger.debug(f"update_order: ({order.asset_code}) {org_order_no} {order_type} {price} {quantity}")
                # 해외주식의 경우 asset_code와 org_order_no를 사용하여 주문을 업데이트
                # 또한 exchange 정보가 들어가지 않음
                return self.trading_api.update_order(order.asset_code, org_order_no, order_type, price, quantity)
            else:
                raise ValueError(f"order not found: {org_order_no}")
        else:
            self.logger.debug(f"update_order: {org_order_no} {order_type} {price} {quantity}")
            return self.trading_api.update_order(org_order_no, order_type, price, quantity, exchange=exchange)

    def cancel_order(self, order_no: str, quantity: int = 0):
        if isinstance(self.trading_api, KISSimpleOverseasStock):
            order = self._get_pending_order(order_no)
            if order is not None:
                self.logger.debug(f"cancel_order: ({order.asset_code}) {order_no} {quantity}")
                return self.trading_api.cancel_order(order.asset_code, order_no, quantity)
            else:
                raise ValueError(f"order not found: {order_no}")

        elif isinstance(self.trading_api, KISSimpleDomesticStock):
            order = self._get_pending_order(order_no, exchanges=[OrderExchange.KRX, OrderExchange.NXT, OrderExchange.SOR])
            if order is not None:
                self.logger.debug(f"cancel_order: {order_no} {quantity} {order.exchange}")
                return self.trading_api.cancel_order(org_order_no=order_no, quantity=quantity, exchange=order.exchange)
            else:
                raise ValueError(f"order not found: {order_no}")
        else:
            # ebest simple에서는 exchange를 사용하지 않음
            self.logger.debug(f"cancel_order: {order_no} {quantity}")
            return self.trading_api.cancel_order(order_no, quantity)

    async def start_classifier(self):
        """ 포지션 분류기를 시작합니다.
        이 메서드는 포지션 분류기를 사용한다면 반드시 호출해야 합니다.
        """
        if self.position_classifier:
            await self.position_classifier.start()


# 백테스팅 할때 사용되는 브로커
class MockBroker(BaseBroker):
    """백테스팅을 위한 가상의 브로커 클래스입니다.

    이 클래스는 과거 데이터를 기반으로 모의 거래를 수행하고 그 결과를 분석할 수 있게 해줍니다.
    가상의 시계를 통해 시간을 제어하며, 실제 시장과 유사한 조건에서의 거래를 시뮬레이션합니다.

    특징:
        - 한국/미국 주식 시장 지원
        - 시장가/지정가/조건부지정가 주문 지원
        - 실제 거래와 동일한 수수료 체계 적용
        - 상세한 거래 이력 관리 및 분석 기능
        - 포지션 추적 및 손익 계산
        - 디버깅을 위한 상세 로깅

    Example:
        >>> # 백테스팅 환경 설정
        >>> clock = WallClock(start_date=date(2023, 1, 1))
        >>> position_provider = MyPositionProvider()
        >>> broker = MockBroker(clock, position_provider, market="kr_stock")
        >>>
        >>> # 초기 자본금 설정
        >>> broker.set_initial_cash(100_000_000)
        >>>
        >>> # 거래 실행
        >>> broker.create_order("005930", OrderSide.BUY, 100, OrderType.LIMIT, 70000)
    """

    LOCAL_CACHE_PATH = "./data"
    """ 데이터 로컬 캐시 경로 """
    DBG_POSTFIX = ""
    """ 디버그 파일 접미사 """
    DEBUG_FILE_PATH = "./debug"
    """ 디버그 파일 저장 경로 """
    logger: Logger
    """ 로깅을 위한 logger 인스턴스 """
    clock: WallClock
    """ 백테스팅 시간 제어를 위한 가상 시계 """
    cash: int
    """ 현재 보유 현금 """
    positions: List[StockPosition]
    """ 현재 보유 중인 포지션 목록 """
    pending_orders: List[StockOrder]
    """ 미체결 주문 목록 """
    trading_history: List[TradingHistory]
    """ 거래 이력 """
    position_provider: BasePositionProvider
    """ 초기 포지션 정보 제공자 """
    time_unit: str
    """ 거래 시간 단위 ("minutes" 또는 "days") """
    market: MarketType
    """ 거래 시장 구분 ("kr_stock" 또는 "us_stock") """
    current_data_handling: Literal["include", "virtual", "exclude"]
    """ 현재 시점의 데이터(e.g. 분봉) 처리 방법 """

    def __init__(
        self,
        clock: WallClock,
        position_provider: BasePositionProvider,
        market: MarketType = "kr_stock",
        time_unit="minutes",
        current_data_handling: Literal["include", "virtual", "exclude"] = "virtual",
        local_cache_path: str = LOCAL_CACHE_PATH,
        market_nxt_on: bool = False,
    ):
        """MockBroker 클래스의 초기화 메서드입니다.

        Args:
            clock (WallClock): 백테스팅 시간을 제어할 가상 시계 객체
            position_provider: 초기 포지션 정보를 제공할 객체
            market (MarketType): 거래 시장 구분 ("kr_stock" 또는 "us_stock")
            time_unit (str, optional): 거래 시간 단위. Defaults to "minutes".
                                    "minutes" 또는 "days" 사용 가능
            current_data_handling (Literal["include", "virtual", "exclude"], optional):
                현재 시점의 데이터(e.g. 분봉) 처리 방법. Defaults to "virtual".
                - "include": 현재(분)까지의 실제 데이터 반환
                - "virtual": 직전(1분전)까지의 데이터 + 현재(분)의 시가로 통일한 가상 데이터 반환 (기본값)
                - "exclude": 직전(1분전)까지의 데이터만 반환
            local_cache_path (str, optional): 데이터 로컬 캐시 경로. Defaults to "./data".
            market_nxt_on (bool, optional): 넥스트레이드 시장 활성화 여부. Defaults to False.
        """
        self.logger = get_logger("MockBroker", clock)
        self.clock = clock
        self.clock.on_time_change = self.on_time_change
        self.market = market
        self.market_nxt_on = market_nxt_on
        self.logger.info(f"init market_nxt_on={self.market_nxt_on}")

        self.next_order_no = 1000
        self.cash = 1_000_000_000
        self.pending_orders: List[StockOrder] = []
        self.trading_history: List[TradingHistory] = []
        self.position_provider = position_provider
        self.positions: List[StockPosition] = position_provider.get_positions(self.clock.today()) if position_provider else []
        self.time_unit = time_unit
        self.current_data_handling = current_data_handling
        self.local_cache_path = local_cache_path

    def set_initial_cash(self, cash):
        """초기 자본금을 설정합니다.

        Args:
            cash (int): 설정할 초기 자본금
        """
        self.cash = cash

    def increase_cash(self, amount):
        self.cash += casting(self.cash, amount)

    def decrease_cash(self, amount):
        self.cash -= casting(self.cash, amount)

    def get_account(self) -> dict:
        """
        계좌 요약 정보를 조회하여 총 잔고, 투자 가능 현금, 매입 금액 및 손익 정보를 반환합니다.
        """
        positions = self.get_positions()

        purchase_amount = sum([p.average_purchase_price * p.quantity for p in positions])
        evaluated_amount = sum([p.current_value for p in positions])
        pnl_amount = evaluated_amount - purchase_amount
        pnl_rate = pnl_amount / purchase_amount * 100 if purchase_amount != 0 else 0

        pending_orders = self.get_pending_orders()
        pending_amount = 0
        for order in pending_orders:
            if order.side == OrderSide.BUY:
                pending_amount += order.price * order.pending_quantity

        total_balance = self.cash + casting(self.cash, evaluated_amount) + casting(self.cash, pending_amount)

        return {
            "total_balance": total_balance,
            "investable_cash": self.cash,
            "purchase_amount": purchase_amount,
            "evaluated_amount": evaluated_amount,
            "pnl_amount": pnl_amount,
            "pnl_rate": pnl_rate,
        }

    def _get_exchange_code(self) -> str:
        """시장 일정을 조회할 때 사용하는 시장 코드를 반환합니다"""
        if self.market == "us_stock":
            return "NYSE"
        else:
            return "KRX"

    def get_price(self, code: str) -> Decimal:
        now = self.clock.now()
        today = now.date()

        def typed_result(value) -> Decimal:
            return Decimal(value).quantize(Decimal("0.0000")) if self.market == "us_stock" else Decimal(int(value))

        market_schedule = get_market_schedule(today, exchange=self._get_exchange_code())
        open_time = market_schedule.open_time
        if self.market_nxt_on:
            try:
                nxt_market_schedule = get_market_schedule(today, exchange="NXT")
                open_time = nxt_market_schedule.open_time
            except ValueError:
                # 2025-03-04 이전 날짜는 ValueError 이므로 무시
                pass

        if now.time() < open_time:
            last_trading_day = get_last_trading_day(today, exchange=self._get_exchange_code())
            df = self.get_daily_price(code, last_trading_day, last_trading_day)  # 전일 종가는 일봉, 분봉 구분이 필요 없다.
            return typed_result(df["close"].iloc[-1])

        else:
            if self.time_unit == "minutes":
                df = self.get_minute_price(code)
                if not df.empty:
                    return typed_result(df["close"].iloc[-1])
                else:
                    # 현재 시간 데이터가 없을 경우 전일 종가로 대체
                    last_trading_day = get_last_trading_day(today, exchange=self._get_exchange_code())
                    df = self.get_daily_price(code, last_trading_day, last_trading_day)  # 전일 종가는 일봉, 분봉 구분이 필요 없다.
                    return typed_result(df["close"].iloc[-1])

            elif self.time_unit == "days":
                df = self.get_daily_price(code, today, today)
                return typed_result(df["close"].iloc[-1])

            else:
                raise ValueError(f"Invalid time unit: {self.time_unit}")

    def get_minute_price(self, code: str) -> pd.DataFrame:
        """
        self.clock 기준 당일의 정규장 시작부터 현재 시각 (이전) 까지의 분봉 데이터를 조회합니다.
        단, market_nxt_on 이면, NXT 가능 종목의 경우 프리마켓, 정규마켓, 애프터마켓의 분봉을 모두 조회합니다.

        Args:
            code (str): 종목 코드

        Returns:
            pd.DataFrame: 분봉 데이터
        """
        today = self.clock.today()
        df = self._get_minute_price_with_cache(today, code)
        if df.empty:
            return df

        # 정규장 정보로만 거르기 ==================================
        market_schedule = get_market_schedule(today, "NYSE" if self.market == "us_stock" else "KRX")
        open_time = dtm.datetime.combine(today, market_schedule.open_time)
        close_time = dtm.datetime.combine(today, market_schedule.close_time)

        # TODO: us_stock 에 대해서는 따로 적용해야 함.
        try:
            nxt_market_schedule = get_market_schedule(today, "NXT")
            is_nxt = df.index[0] == dtm.datetime.combine(today, nxt_market_schedule.open_time)
            if self.market_nxt_on and is_nxt:
                open_time = dtm.datetime.combine(today, nxt_market_schedule.open_time)
                close_time = dtm.datetime.combine(today, nxt_market_schedule.close_time)
        except ValueError:
            # 2025-03-04 이전 날짜는 ValueError 이므로 무시
            pass

        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        df = df[(df.index >= open_time) & (df.index <= close_time)]
        # ========================================================

        # 미래 정보 없애기
        now = pd.Timestamp(self.clock.now())
        include_df = df[df.index <= now].copy()
        if include_df.empty:
            return include_df

        if self.current_data_handling == "include":
            return include_df
        else:
            min_ago = min(now, close_time) - pd.Timedelta(minutes=1)
            exclude_df = df[df.index <= min_ago].copy()
            last_minute_df = include_df.iloc[-1]
            last_minute_df = last_minute_df.to_frame().T

            if self.current_data_handling == "exclude":
                if now <= close_time:
                    return exclude_df
                else:
                    return pd.concat([exclude_df, last_minute_df])
            elif self.current_data_handling == "virtual":
                # 정규장 종료 시각 이전은 N분 0초 기준으로 해당 분의 시가로 통일함
                # 다만, 정규장 종료 시각 이후는 동시호가 시장가 종가로 체결되므로 원 데이터를 그대로 사용함
                if now < close_time:
                    current_price = last_minute_df["open"].iloc[0]
                    virtual_data = {
                        "open": current_price,
                        "high": current_price,
                        "low": current_price,
                        "close": current_price,
                        "volume": 1,
                        "value": 1,
                        "cum_volume": exclude_df["cum_volume"].iloc[-1] if not exclude_df.empty else 1,
                        "cum_value": exclude_df["cum_value"].iloc[-1] if not exclude_df.empty else 1,
                    }
                    last_minute_df = pd.DataFrame([virtual_data], index=[last_minute_df.index[0]])
                return pd.concat([exclude_df, last_minute_df])
            else:
                raise ValueError(f"Invalid current_data_handling: {self.current_data_handling}")

    @lru_cache(maxsize=40)
    def _get_minute_price_with_cache(self, date, code) -> pd.DataFrame:
        """
        market_nxt_on 이면, NXT 프리마켓, 정규마켓, 애프터마켓의 분봉이 모두 반환된다.
        """
        folder_name = "nxt_minutes" if self.market_nxt_on else "minutes"
        file_path = f"{self.local_cache_path}/{folder_name}/{date}/{code}.csv" if self.local_cache_path else None
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        df = pd.read_csv(f)
                        df['time'] = pd.to_datetime(df['time'])
                        df.set_index('time', inplace=True)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                self.logger.exception(e)
                if os.path.exists(file_path):
                    os.remove(file_path)
                df = self._fetch_minute_price(date, code)
        else:
            df = self._fetch_minute_price(date, code)

        return df

    def _fetch_minute_price(self, date, code) -> pd.DataFrame:
        folder_name = "nxt_minutes" if self.market_nxt_on else "minutes"
        file_path = f"{self.local_cache_path}/{folder_name}/{date}/{code}.csv" if self.local_cache_path else None

        if self.market == "us_stock":
            dfs = get_us_minute_data(date, [code])
        else:
            if self.market_nxt_on:
                # NXT 에 해당 종목이 없는 경우 KRX 의 결과값을 반환한다. 하지만 로컬 캐시 폴더는 NXT 기준으로 저장한다.
                dfs = get_kr_minute_data(date, [code], dtm.timedelta(minutes=1), source="kis", adjusted=True, exchange=DataExchange.KRX)
                dfs_nxt = get_kr_minute_data(date, [code], dtm.timedelta(minutes=1), source="kis", adjusted=True, exchange=DataExchange.NXT)
                if code in dfs_nxt and not dfs_nxt[code].empty:
                    _df = dfs[code]
                    _df_nxt = dfs_nxt[code]
                    common_dates = _df.index.intersection(_df_nxt.index)
                    for _date in common_dates:
                        _df_nxt.loc[_date, 'volume'] = _df.loc[_date, 'volume'] + _df_nxt.loc[_date, 'volume']
                        _df_nxt.loc[_date, 'value'] = _df.loc[_date, 'value'] + _df_nxt.loc[_date, 'value']
                        _df_nxt.loc[_date, 'cum_volume'] = _df.loc[_date, 'cum_volume'] + _df_nxt.loc[_date, 'cum_volume']
                        _df_nxt.loc[_date, 'cum_value'] = _df.loc[_date, 'cum_value'] + _df_nxt.loc[_date, 'cum_value']
                        # 한투 앱에서 통합 차트의 경우 KRX값이 우선으로 사용됨
                        _df_nxt.loc[_date, 'open'] = _df.loc[_date, 'open']
                        _df_nxt.loc[_date, 'high'] = max(_df.loc[_date, 'high'], _df_nxt.loc[_date, 'high'])
                        _df_nxt.loc[_date, 'low'] = min(_df.loc[_date, 'low'], _df_nxt.loc[_date, 'low'])
                        _df_nxt.loc[_date, 'close'] = _df.loc[_date, 'close']

                    # 15:30 이후의 cum_volume, cum_value는 15:30의 cum_volume, cum_value에다가 _df_nxt의 15:31 부터 각 volume, value를 매분 누적하여 저장
                    market_close_datetime = dtm.datetime.combine(date, get_market_schedule(date, "KRX").close_time)
                    if market_close_datetime in _df_nxt.index:
                        base_cum_volume = _df_nxt.loc[market_close_datetime, 'cum_volume']
                        base_cum_value = _df_nxt.loc[market_close_datetime, 'cum_value']

                        # 15:31 이후 데이터에 대해 누적 계산
                        after_market_close = _df_nxt.index > market_close_datetime
                        if after_market_close.any():
                            for idx in _df_nxt[after_market_close].index:
                                _df_nxt.loc[idx, 'cum_volume'] = base_cum_volume + _df_nxt.loc[idx, 'volume']
                                _df_nxt.loc[idx, 'cum_value'] = base_cum_value + _df_nxt.loc[idx, 'value']
                                base_cum_volume = _df_nxt.loc[idx, 'cum_volume']
                                base_cum_value = _df_nxt.loc[idx, 'cum_value']

                    dfs[code] = _df_nxt
            else:
                dfs = get_kr_minute_data(date, [code], dtm.timedelta(minutes=1), source="kis", adjusted=True, exchange=DataExchange.KRX)

        df = dfs[code]
        if df.empty:
            return df

        if self.local_cache_path:
            if not os.path.exists(f"{self.local_cache_path}/{folder_name}/{date}"):
                os.makedirs(f"{self.local_cache_path}/{folder_name}/{date}")

            df.reset_index(inplace=True)
            with open(file_path, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    df.to_csv(f, index=False)
                except Exception as e:
                    self.logger.exception(e)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            df.set_index("time", inplace=True)

        return df

    def get_daily_price(self, code: str, from_date: Optional[dtm.date] = None, end_date: Optional[dtm.date] = None):
        """
        지정된 기간 동안의 정규장 시작부터 현재 시각 (이전) 까지의 일봉 데이터를 조회합니다.
        단, market_nxt_on 이면, NXT 가능 종목의 경우 프리마켓, 정규마켓, 애프터마켓의 일봉을 모두 조회합니다.
        """
        today = self.clock.today()

        def _exclude_today(df: pd.DataFrame) -> pd.DataFrame:
            if self.market == "kr_stock":
                return df[df.index < pd.Timestamp(today)]
            elif self.market == "us_stock":
                return df[df.index < pd.Timestamp(today).date()]
            else:
                raise ValueError(f"Invalid market: {self.market}")

        if from_date is None:
            from_date = get_trading_day_with_offset(today, -10, exchange=self._get_exchange_code())
        if end_date is None:
            end_date = today

        if self.market == "us_stock":
            dfs = get_us_daily_data([code], from_date, end_date, adjusted=True, ascending=True)
        else:
            if self.market_nxt_on:
                dfs = get_kr_daily_data([code], from_date, end_date, adjusted=True, ascending=True, exchange=DataExchange.KRX)
                dfs_nxt = get_kr_daily_data([code], from_date, end_date, adjusted=True, ascending=True, exchange=DataExchange.NXT)
                if code in dfs_nxt:
                    _df = dfs[code]
                    _df_nxt = dfs_nxt[code]

                    # 같은 날짜의 데이터만 volume과 value를 합치고, open, close는 NXT 값으로 교체
                    common_dates = _df.index.intersection(_df_nxt.index)
                    for _date in common_dates:
                        _df.loc[_date, 'volume'] = _df.loc[_date, 'volume'] + _df_nxt.loc[_date, 'volume']
                        _df.loc[_date, 'value'] = _df.loc[_date, 'value'] + _df_nxt.loc[_date, 'value']
                        _df.loc[_date, 'open'] = _df_nxt.loc[_date, 'open']
            else:
                dfs = get_kr_daily_data([code], from_date, end_date, adjusted=True, ascending=True, exchange=DataExchange.KRX)

        df = dfs[code]

        if not df.empty and end_date == today:
            # 마지막 데이터가 오늘인 경우 장중 여부와 설정에따라 구분되어 처리될 필요가 있다.
            now = self.clock.now()
            schedule = get_market_schedule(today, exchange=self._get_exchange_code())
            open_time = schedule.open_time
            close_time = schedule.close_time
            if self.market_nxt_on:
                try:
                    nxt_schedule = get_market_schedule(today, "NXT")
                    open_time = nxt_schedule.open_time
                    close_time = nxt_schedule.close_time
                except ValueError:
                    # 2025-03-04 이전 날짜는 ValueError 이므로 무시
                    pass

            if schedule.full_day_closed:
                pass  # end_date 가 폐장일이면 해당 날짜의 데이터는 이미 없음
            else:
                if self.current_data_handling == "include":
                    pass
                elif self.current_data_handling == "virtual":
                    if now.time() < open_time:
                        # 장 오픈 전은 전일 데이터 까지만 반환
                        df = _exclude_today(df)
                    elif now.time() <= close_time:
                        # 장중에는 분봉을 적절히 활용
                        minute_df = self.get_minute_price(code)
                        if minute_df.empty:
                            df = _exclude_today(df)
                        else:
                            # 현재까지의 분봉 df 를 이용해 오늘의 ohlcv 를 생성
                            today_index = pd.Timestamp(today) if self.market == "kr_stock" else pd.Timestamp(today).date()
                            today_ohlcv = pd.Series(
                                {
                                    "open": minute_df.iloc[0]["open"],
                                    "high": minute_df["high"].max(),
                                    "low": minute_df["low"].min(),
                                    "close": minute_df.iloc[-1]["close"],
                                    "volume": minute_df.iloc[-1]["cum_volume"],
                                    "value": minute_df.iloc[-1]["cum_value"],
                                },
                                name=today_index,
                            )

                            # 오늘 데이터를 새로운 OHLCV로 교체
                            df.loc[today_index] = today_ohlcv
                    else:
                        # 정규장 마감 이후는 조회된 일봉 그대로 반환
                        pass
                elif self.current_data_handling == "exclude":
                    df = _exclude_today(df)
        return df

    def get_pending_orders(self, exchanges: List[OrderExchange] = [OrderExchange.KRX]):
        # MockBroker 에서는 SOR, NXT 주문을 현재 구분하지 않음.
        return self.pending_orders

    def get_positions(self):
        for p in self.positions:
            price = self.get_price(p.asset_code)
            p.current_price = price
            p.current_value = price * p.quantity
            p.current_pnl_value = int((price - p.average_purchase_price) * p.quantity)
            p.current_pnl = Decimal(0) if p.quantity == 0 else Decimal((p.current_pnl_value / (p.average_purchase_price * p.quantity)) * 100).quantize(Decimal("0.00"))

        positions = [p for p in self.positions if p.quantity > 0]
        return positions

    def create_order(self, asset_code: str, side: OrderSide, quantity: int, order_type: OrderType = OrderType.MARKET, price: int = 0, exchange: OrderExchange = OrderExchange.KRX) -> str:
        price = self.get_price(asset_code) if order_type == OrderType.MARKET else price
        self.logger.info(f"CREATE ORDER: {self._get_asset_name(asset_code)} side:{side} price:{price} quantity:{quantity} order_type:{order_type} exchange:{exchange.value}")
        order_no = str(self.next_order_no)
        self.next_order_no += 1

        if side is OrderSide.BUY:
            total_amount = int(price * quantity)
            if self.cash < total_amount:
                raise ValueError("not enough cash")
            else:
                self.decrease_cash(total_amount)

        if isinstance(price, np.int64):
            raise ValueError(f"price must be int, not np.int64: {price} {type(price)}")

        order = StockOrder(
            order_no=order_no,
            asset_code=asset_code,
            side=side,
            price=price,
            quantity=quantity,
            filled_quantity=0,
            pending_quantity=quantity,
            order_type=order_type,
            order_time=self.clock.now(),
            exchange=exchange,
        )

        self.pending_orders.append(order)
        self.logger.info(f"ORDER CREATED: {order}\n{self.pending_orders}")

        return order_no

    def update_order(self, org_order_no: str, order_type: OrderType, price: int, quantity: int = 0, exchange: OrderExchange = OrderExchange.KRX):
        order = next((order for order in self.pending_orders if order.order_no == org_order_no), None)
        if order is None:
            raise Exception(f"order not found: {org_order_no}")

        if quantity > order.pending_quantity:
            raise ValueError("quantity must be less than pending quantity")

        if quantity == 0:
            quantity = order.pending_quantity

        if order.side == OrderSide.BUY:
            price_diff = price - order.price
            diff_value = int(price_diff * quantity)
            if self.cash < diff_value:
                raise ValueError("not enough cash")
            else:
                self.decrease_cash(diff_value)

        new_order_no = str(self.next_order_no)
        self.next_order_no += 1

        new_order = StockOrder(
            org_order_no=order.order_no,
            order_no=new_order_no,
            asset_code=order.asset_code,
            side=order.side,
            price=price,
            quantity=quantity,
            filled_quantity=0,
            pending_quantity=quantity,
            order_type=order_type,
            order_time=self.clock.now(),
            exchange=exchange,
        )

        order.pending_quantity -= quantity
        self.pending_orders = [o for o in self.pending_orders if o.pending_quantity > 0]
        self.pending_orders.append(new_order)

    def cancel_order(self, order_no: str, quantity: int = 0):
        order = next((order for order in self.pending_orders if order.order_no == order_no), None)
        if order is None:
            raise Exception(f"order not found: {order_no}")

        if quantity == 0:
            self.pending_orders = [o for o in self.pending_orders if o.order_no != order_no]
        else:
            order.pending_quantity -= quantity
            if order.pending_quantity == 0:
                self.pending_orders = [o for o in self.pending_orders if o.order_no != order_no]

        if order.side == OrderSide.BUY:
            if quantity == 0:
                quantity = order.pending_quantity
            self.increase_cash(int(order.price * quantity * 1.00015))

    def _cancel_order(self, order: StockOrder):
        """
        on_time_change에서 데이터 누락 등의 오류 상황일 때 미리 뺀 cash를 원복한다.
        """
        if order.side == OrderSide.BUY:
            self.increase_cash(int(order.price * order.pending_quantity))

        self.pending_orders = [o for o in self.pending_orders if o.order_no != order.order_no]

    def on_time_change(self, current_time, before_time):
        self.get_positions()  # self.positions 에 있는 포지션들의 현재 가격을 조회하여 업데이트 함

        today = current_time.date()
        market_schedule = get_market_schedule(today, exchange=Exchange.KRX)

        open_time = dtm.datetime.combine(today, market_schedule.open_time)
        close_time = dtm.datetime.combine(today, market_schedule.close_time)
        preclose_auction_start_time = close_time - dtm.timedelta(minutes=10)

        try:
            nxt_market_schedule = get_market_schedule(today, exchange=Exchange.NXT)
        except ValueError:
            nxt_market_schedule = market_schedule
        nxt_pre_open_time = dtm.datetime.combine(today, nxt_market_schedule.open_time)
        nxt_pre_close_time = nxt_pre_open_time + dtm.timedelta(minutes=50)
        # nxt_main_open_time = dtm.datetime.combine(today, open_time) + dtm.timedelta(seconds=30)
        # nxt_main_close_time = close_time - dtm.timedelta(minutes=10)
        nxt_after_open_time = close_time
        nxt_after_close_time = dtm.datetime.combine(today, nxt_market_schedule.close_time)

        just_closed = current_time.replace(second=0, microsecond=0) == close_time.replace(second=0, microsecond=0)
        if preclose_auction_start_time - dtm.timedelta(minutes=1) <= current_time <= preclose_auction_start_time + dtm.timedelta(minutes=1):
            # 로그 출력 수 조정
            self.logger.debug(f"just_closed: {just_closed} {self.pending_orders}")

        if market_schedule.full_day_closed or current_time < open_time or (current_time > close_time and not just_closed):
            if self.market_nxt_on and not market_schedule.full_day_closed:
                # market_nxt_on 인 경우 메인 마켓은 KRX 그대로 사용하고 프리마켓과 애프터마켓만 추가한다.
                if current_time < nxt_pre_open_time or nxt_pre_close_time <= current_time < open_time or close_time < current_time < nxt_after_open_time or nxt_after_close_time <= current_time:
                    self.logger.warning(f"on_time_change(nxt_on): {before_time} ~ {current_time} market is closed")
                    return
            else:
                self.logger.warning(f"on_time_change: {before_time} ~ {current_time} market is closed")
                return

        for order in list(self.pending_orders):
            if self.time_unit == "minutes":
                if preclose_auction_start_time <= current_time < close_time:
                    self.logger.info(f"ORDER SKIPPED: {order.asset_code} preclose auction time")
                    continue

                if current_time < close_time and current_time - before_time < dtm.timedelta(seconds=60):
                    # 강제로 1분 차이를 만들어 줌
                    before_time = current_time - dtm.timedelta(seconds=60)

                if self.market_nxt_on and current_time < nxt_after_close_time and current_time - before_time < dtm.timedelta(seconds=60):
                    # 강제로 1분 차이를 만들어 줌
                    before_time = current_time - dtm.timedelta(seconds=60)

                df = self.get_minute_price(order.asset_code)
                if df.empty:
                    self.logger.warning(f"ORDER CANCELED: {order.asset_code} minute data is empty")
                    self._cancel_order(order)
                    continue

                df = df[(df.index >= before_time) & (df.index <= current_time)].copy()
                if df.empty:
                    self.logger.warning(f"ORDER CANCELED: {order.asset_code} minute range data is empty: {before_time} ~ {current_time}")
                    self._cancel_order(order)
                    continue

            elif self.time_unit == "days":
                from_date = before_time.date()
                to_date = current_time.date()

                df = self.get_daily_price(order.asset_code, from_date, to_date)
                if df.empty:
                    self.logger.info(f"ORDER CANCELED: {order.asset_code} daily data is empty")
                    self._cancel_order(order)
                    continue

            else:
                self._cancel_order(order)
                raise ValueError(f"Invalid time unit: {self.time_unit}")

            if df["volume"].iloc[-1] == 0 and current_time != close_time:
                self.logger.info(f"ORDER CANCELED: {order.asset_code} volume is 0")
                self._cancel_order(order)
                continue

            if "cvolume" in df.columns and df["cvolume"].iloc[-1] == 0:
                self.logger.info(f"ORDER CANCELED: {order.asset_code} cvolume is 0")
                self._cancel_order(order)
                continue

            if "cum_volume" in df.columns and df["cum_volume"].iloc[-1] == 0:
                self.logger.info(f"ORDER CANCELED: {order.asset_code} cum_volume is 0")
                self._cancel_order(order)
                continue

            if order.order_type in (OrderType.LIMIT, OrderType.LIMIT_FOK, OrderType.LIMIT_IOC) or (order.order_type == OrderType.LIMIT_CONDITIONAL and current_time < close_time):
                # 지정가 종류의 주문은 백테스트의 경우 모두 OrderType.LIMIT 과 같이 동작
                df = df[(df.index >= (before_time - dtm.timedelta(seconds=60))) & (df.index <= current_time)].copy()
                self.logger.debug(f"on_time_change {before_time} => {current_time} asset_code={order.asset_code} df:\n{df}")
                if df.empty:
                    self.logger.info(f"ORDER CANCELED: {order.asset_code} no data")
                    self._cancel_order(order)
                    continue

                high = int(df["high"].max())
                low = int(df["low"].min())
                # close = int(df["close"].iloc[-1])

                filled_price = None

                if order.side == OrderSide.BUY:
                    if order.price > high:
                        filled_price = high
                    elif order.price < low:
                        # not fill
                        self.logger.info(f"BUY ORDER NOT FILLED: {self._get_asset_name(order.asset_code)} price:{order.price} low:{low}")
                        pass
                    else:
                        filled_price = order.price

                elif order.side == OrderSide.SELL:
                    if order.price > high:
                        # not fill
                        self.logger.info(f"SELL ORDER NOT FILLED: {self._get_asset_name(order.asset_code)} price:{order.price} high:{high}")
                        pass
                    elif order.price < low:
                        filled_price = low
                    else:
                        filled_price = order.price

                order.quantity = int(order.quantity)
                if filled_price and order.quantity:
                    filled_price = int(filled_price)
                    if order.side == OrderSide.BUY:
                        self._buy_position(order.order_no, order.asset_code, order.quantity, filled_price, current_time)
                    elif order.side == OrderSide.SELL:
                        self._sell_position(order.order_no, order.asset_code, order.quantity, filled_price, current_time)

            else:
                # 지정가 종류 이외에는 모두 시장가 주문으로 간주하고 OrderType.MARKET 과 같이 동작 (단, 조건부지정가는 장마감 시 시장가 주문으로 간주)
                df = df[(df.index >= before_time) & (df.index <= current_time)].copy()
                self.logger.debug(f"on_time_change {before_time} => {current_time} asset_code={order.asset_code} df:\n{df}")

                if df.empty:
                    self.logger.info(f"ORDER CANCELED: {order.asset_code} no data")
                    self._cancel_order(order)
                    continue

                filled_price = int(df["close"].iloc[-1])

                order.quantity = int(order.quantity)
                if order.quantity:
                    self.logger.info(f"ORDER FILLED: {order.asset_code}, price:{filled_price}, quantity:{order.quantity}, side:{order.side}, current_time:{current_time}, before_time:{before_time}")
                    if order.side == OrderSide.BUY:
                        self._buy_position(order.order_no, order.asset_code, order.quantity, filled_price, current_time)
                    else:
                        self._sell_position(order.order_no, order.asset_code, order.quantity, filled_price, current_time)

    def _sell_position(self, order_no: str, asset_code: str, quantity: int, price: int, executed_time: dtm.datetime):
        self.logger.info(f"SELL POSITION: {asset_code} price:{price} quantity:{quantity}\n{self.positions}")
        for pos in self.positions:
            if pos.asset_code == asset_code:
                pos.quantity -= quantity
                pos.quantity = max(0, pos.quantity)
                pos.sell_possible_quantity -= quantity
                pos.sell_possible_quantity = max(0, pos.sell_possible_quantity)
                pos.current_value = pos.current_price * pos.quantity
                pos.current_pnl_value = (pos.current_price - pos.average_purchase_price) * pos.quantity
                pos.current_pnl = Decimal(0) if pos.quantity == 0 else Decimal(pos.current_pnl_value / (pos.average_purchase_price * pos.quantity) * 100).quantize(Decimal("0.00"))

                sell_value = price * quantity

                # 시장별 수수료 및 세금 계산
                if self.market == "us_stock":
                    tax = 0  # 미국 주식은 매도 시 거래세 없음
                    fee = sell_value * Decimal("0.00025")  # 수수료 0.025%
                else:
                    tax = sell_value * Decimal("0.0023")  # 거래세 0.23%
                    fee = sell_value * Decimal("0.00015")  # 수수료 0.015%

                buy_value = pos.average_purchase_price * quantity
                buy_fee = buy_value * Decimal(0.00015)
                pnl = sell_value - buy_value - fee - tax - buy_fee
                pnl_rate = pnl / buy_value * 100 if buy_value != 0 else 0

                self.add_trading_history(
                    TradingHistory(
                        date=self.clock.today().strftime("%Y%m%d"),
                        order_no=order_no,
                        side=OrderSide.SELL,
                        asset_code=asset_code,
                        quantity=quantity,
                        filled_price=price,
                        average_purchase_price=pos.average_purchase_price,
                        tax=tax,
                        fee=fee,
                        pnl=pnl,
                        pnl_rate=pnl_rate,
                        executed_time=int(executed_time.timestamp() * 1000),
                    )
                )

                self.increase_cash(sell_value - fee - tax)

        self.positions = [p for p in self.positions if p.quantity > 0]
        self.pending_orders = [o for o in self.pending_orders if o.order_no != order_no]

    def _buy_position(self, order_no: str, asset_code: str, quantity: int, price: int, executed_time: dtm.datetime):
        self.logger.info(f"BUY POSITION: {asset_code} price:{price} quantity:{quantity}\n{self.positions}")
        if quantity is None or quantity < 1:
            self.logger.error(f"BUY_POSITION: quantity must be greater than 0: {quantity}")
            return

        if price is None or price <= 0:
            self.logger.error(f"BUY_POSITION: price must be greater than 0: {price}")
            return

        found = False
        for pos in self.positions:
            if pos.asset_code == asset_code:
                pos.average_purchase_price = (pos.average_purchase_price * pos.quantity + price * quantity) / Decimal(str(pos.quantity + quantity))

                pos.quantity += quantity
                pos.sell_possible_quantity += quantity
                pos.current_value = pos.current_price * pos.quantity
                pos.current_pnl_value = (pos.current_price - pos.average_purchase_price) * pos.quantity
                pos.current_pnl = Decimal(0) if pos.quantity == 0 else Decimal(pos.current_pnl_value / (pos.average_purchase_price * pos.quantity) * 100).quantize(Decimal("0.00"))
                found = True
                break

        if not found:
            pos = StockPosition(
                asset_code=asset_code,
                asset_name=self._get_asset_name(asset_code),
                quantity=quantity,
                sell_possible_quantity=quantity,
                average_purchase_price=Decimal(price),
                current_price=price,
                current_value=price * quantity,
                current_pnl=Decimal(0),
                current_pnl_value=0,
            )
            self.positions.append(pos)

        order = next((order for order in self.pending_orders if order.order_no == order_no), None)
        order_buy_value = order.price * order.pending_quantity

        buy_value = price * quantity

        # 시장별 수수료 계산
        if self.market == "us_stock":
            fee = buy_value * Decimal("0.00025")  # 수수료 0.025%
        else:
            fee = buy_value * Decimal("0.00015")  # 수수료 0.015%

        # 주문가와 체결가가 다를 수 있음
        if order_buy_value != buy_value:
            diff_amount = order_buy_value - buy_value
            self.increase_cash(diff_amount)

        self.add_trading_history(
            TradingHistory(
                date=self.clock.today().strftime("%Y%m%d"),
                order_no=order_no,
                side=OrderSide.BUY,
                asset_code=asset_code,
                quantity=quantity,
                filled_price=price,
                average_purchase_price=Decimal(price),
                fee=fee,
                tax=0,
                pnl=0,
                pnl_rate=0,
                executed_time=int(executed_time.timestamp() * 1000),
            )
        )

        self.pending_orders = [o for o in self.pending_orders if o.order_no != order_no]

    def add_trading_history(self, history):
        self.trading_history.append(history)

    def show_trading_history_report(self, make_file: bool = False, filter_side: OrderSide = None, sort: str = None, invested_capital: int = 0):
        """거래 이력 보고서를 생성하고 표시합니다.

        Args:
            make_file (bool, optional): CSV 파일로 저장할지 여부. Defaults to False.
            filter_side (OrderSide, optional): 특정 거래 방향(매수/매도)으로 필터링. Defaults to None.
            sort (str, optional): 정렬 기준. Defaults to None.

        Returns:
            dict: 거래 분석 결과를 포함하는 딕셔너리
                - count (int): 총 거래 건수
                - sum_pnl_rate (float): 손익률 합
                - avg_pnl_rate (float): 평균 손익률
                - avg_max_pnl_rate (float): 평균 최고 손익률
                - avg_min_pnl_rate (float): 평균 최저 손익률
                - sum_buy_value (int): 총 매수 금액
                - sum_pnl_value (int): 총 손익 금액
                - roi_rate (float): 투자수익률 (ROI(%))

        Note:
            CSV 파일은 DEBUG_FILE_PATH 경로에 저장되며,
            파일명은 날짜와 시간을 포함합니다.
        """
        empty_ret = {
            "count": 0,
            "sum_pnl_rate": 0,
            "avg_pnl_rate": 0,
            "avg_max_pnl_rate": 0,
            "avg_min_pnl_rate": 0,
            "sum_buy_value": 0,
            "sum_pnl_value": 0,
            "roi_rate": 0,
        }
        if len(self.trading_history) == 0:
            return empty_ret

        dict_list = []
        for trade in self.trading_history:
            d = asdict(trade)

            if filter_side and d["side"] != filter_side:
                continue

            d["side"] = "BUY" if d["side"] == OrderSide.BUY else "SELL"
            d["name"] = self._get_asset_name(d["asset_code"])
            d["time"] = dtm.datetime.fromtimestamp(d["executed_time"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            d["buy_value"] = d["average_purchase_price"] * d["quantity"]

            d.pop("executed_time")
            d.pop("date")
            d.pop("partial")

            d["average_purchase_price"] = d["average_purchase_price"].quantize(Decimal("0.00"))
            d["buy_value"] = int(d["buy_value"]) if d["buy_value"] else 0
            d["tax"] = int(d["tax"]) if d["tax"] else 0
            d["fee"] = int(d["fee"]) if d["fee"] else 0
            d["pnl"] = int(d["pnl"]) if d["pnl"] else 0
            d["pnl_rate"] = d["pnl_rate"].quantize(Decimal("0.00")) if d["pnl_rate"] else Decimal("0.00")

            minute_data = self.get_minute_price(d["asset_code"])
            if not minute_data.empty:
                d["max_price"] = minute_data["high"].max()
                d["max_time"] = minute_data["high"].idxmax()
                d["max_pnl_rate"] = (Decimal(str(d["max_price"])) - d["average_purchase_price"]) / d["average_purchase_price"] * 100
                d["max_pnl_rate"] = d["max_pnl_rate"].quantize(Decimal("0.00"))

                d["min_price"] = minute_data["low"].min()
                d["min_time"] = minute_data["low"].idxmin()
                d["min_pnl_rate"] = (Decimal(str(d["min_price"])) - d["average_purchase_price"]) / d["average_purchase_price"] * 100
                d["min_pnl_rate"] = d["min_pnl_rate"].quantize(Decimal("0.00"))

                date = dtm.datetime.strptime(d["time"], "%Y-%m-%d %H:%M:%S").date()
                prev_date = get_last_trading_day(date)
                # 전일 시가총액
                try:
                    dft = get_market_cap_by_codes([d["asset_code"]], prev_date)
                    d["market_cap"] = round(dft["value"].iloc[-1] / 100000000)
                except Exception as e:
                    self.logger.error(f"get_market_cap error: {d['asset_code']} {d['name']} {prev_date} {e}")
                    d["market_cap"] = 0

                # 전일 거래대금
                try:
                    dft = get_kr_daily_data([d["asset_code"]], prev_date, prev_date)[d["asset_code"]]
                    d["prev_value"] = round(dft["value"].iloc[-1] / 100000000)
                except Exception as e:
                    self.logger.error(f"전일거래대금 error: {d['asset_code']} {d['name']} {prev_date} {e}")
                    d["prev_value"] = 0
                dict_list.append(d)

        df = pd.DataFrame(dict_list)
        if df.empty:
            return empty_ret

        df.set_index("time", inplace=True)
        df = df.sort_values(by="time")

        if make_file:
            # BacktestEnvironment의 end_time이 휴장일인 경우 분봉 데이터가 없음
            if not minute_data.empty:
                df = df.sort_values(by="max_buy_rate", ascending=False)

            filename = f"{self.DEBUG_FILE_PATH}/trading_history_{self.clock.today().strftime('%Y%m%d')}_{int(dtm.datetime.now().timestamp())}_{self.DBG_POSTFIX}.csv"
            try:
                df.to_csv(filename)
            except IOError:
                os.makedirs(self.DEBUG_FILE_PATH, exist_ok=True)
                df.to_csv(filename)

        if not sort:
            df = df.sort_index()
        else:
            df = df.sort_values(by=sort, ascending=False)

        df.rename(
            columns={
                "order_no": "주문번호",
                "asset_code": "종목코드",
                "name": "종목명",
                "side": "매매구분",
                "quantity": "수량",
                "filled_price": "체결가",
                "average_purchase_price": "평단가",
                "buy_value": "매수금액",
                "tax": "세금",
                "fee": "수수료",
                "pnl": "손익금액",
                "pnl_rate": "손익률(%)",
                "max_price": "최고가",
                "max_time": "고가시간",
                "max_pnl_rate": "고가손익률(%)",
                "min_price": "최저가",
                "min_time": "저가시간",
                "min_pnl_rate": "저가손익률(%)",
                "market_cap": "시가총액",
                "prev_value": "전일거래대금",
            },
            inplace=True,
        )
        df.index.name = "체결시간"

        pd.set_option("display.max_rows", None)
        # 컬럼 순서 변경
        df = df[
            [
                "주문번호",
                "종목코드",
                "종목명",
                "매매구분",
                "수량",
                "체결가",
                "평단가",
                "매수금액",
                "세금",
                "수수료",
                "손익금액",
                "손익률(%)",
                "최고가",
                "고가시간",
                "고가손익률(%)",
                "최저가",
                "저가시간",
                "저가손익률(%)",
                "시가총액",
                "전일거래대금",
            ]
        ]
        # df = df[['종목코드', '수량', '체결가', '평단가', '매수금액', '세금', '수수료', '손익금액', '손익률(%)', '최고가', '고가시간', '고가손익률(%)', '최저가', '저가시간', '저가손익률(%)', '시가총액', '전일거래대금', '종목명']]
        df["고가시간"] = df["고가시간"].dt.strftime("%H:%M:%S")
        df["저가시간"] = df["저가시간"].dt.strftime("%H:%M:%S")
        self.logger.info(f"\n{df}")
        pd.reset_option("display.max_rows")

        count = len(df)
        sum_pnl_rate = df["손익률(%)"].sum()
        avg_pnl_rate = df["손익률(%)"].mean()
        avg_max_pnl_rate = df["고가손익률(%)"].mean()
        avg_min_pnl_rate = df["저가손익률(%)"].mean()
        sum_buy_value = df["매수금액"].sum()
        sum_pnl_value = df["손익금액"].sum()
        roi_rate = sum_pnl_value / invested_capital * 100 if invested_capital != 0 else 0

        datestr = self.clock.today().strftime("%Y%m%d")
        self.logger.info(
            f"{datestr} Total {count} trades, Sum PnL(%): {sum_pnl_rate:7.2f}%, Avg PnL/Max/Min(%):{avg_pnl_rate:>7.2f}%/{avg_max_pnl_rate:>7.2f}%/{avg_min_pnl_rate:>7.2f}% Earn/Buy={sum_pnl_value:9.0f}/{sum_buy_value:9.0f} INVESTED_CAPITAL={invested_capital:>9,.0f} ROI(%):{roi_rate:>7.2f}%"
        )

        return {
            "count": count,
            "sum_pnl_rate": sum_pnl_rate,
            "avg_pnl_rate": avg_pnl_rate,
            "avg_max_pnl_rate": avg_max_pnl_rate,
            "avg_min_pnl_rate": avg_min_pnl_rate,
            "sum_buy_value": sum_buy_value,
            "sum_pnl_value": sum_pnl_value,
            "roi_rate": roi_rate,
        }

    def show_positions(self, sort: str = None):
        """현재 보유 중인 포지션 현황을 표시합니다.

        Args:
            sort (str, optional): 정렬 기준. Defaults to None.

        Returns:
            dict: 포지션 분석 결과를 포함하는 딕셔너리
                - buy_value (int): 총 매수 금액
                - pnl_value (int): 총 평가 손익
                - pnl (float): 총 수익률(%)
                - current_value (int): 현재 평가 금액
        """
        positions = [p for p in self.positions if p.quantity > 0]
        data = []
        buy_value = 0
        pnl_value = 0
        current_value = 0
        pnl_rate = 0

        for pos in positions:
            d = asdict(pos)
            d["average_purchase_price"] = round(float(pos.average_purchase_price), 2) if pos.average_purchase_price else 0
            d["current_pnl_value"] = int(pos.current_pnl_value)
            data.append(d)

            buy_value += d["average_purchase_price"] * d["quantity"]
            pnl_value += d["current_pnl_value"]
            current_value += d["current_value"]

        df = pd.DataFrame(data)

        if len(df) > 0:
            pnl_rate = pnl_value / buy_value * 100 if buy_value != 0 else 0
            if not sort:
                df = df.sort_index()
            else:
                sort = "current_pnl" if sort == "pnl_rate" else sort
                df = df.sort_values(by=sort, ascending=False)
            self.logger.debug(f"\n{df[['asset_code', 'quantity', 'sell_possible_quantity', 'average_purchase_price', 'current_price', 'current_value', 'current_pnl', 'current_pnl_value', 'asset_name']]}")
            self.logger.info(f"Total Buy Value: {buy_value} Total PnL: {pnl_value} ({pnl_rate}%)")

        return {"buy_value": buy_value, "pnl_value": pnl_value, "pnl_rate": pnl_rate, "current_value": current_value}

    @lru_cache
    def _get_asset_name(self, code: str):
        if self.market == "us_stock":
            df = get_us_ticker_info(code)
        else:
            df = get_kr_ticker_info(code)
        return df["name"].iloc[-1]


if __name__ == "__main__":
    from pyqqq.backtest.positionprovider import ManualPositionProvider

    clock = WallClock(live_mode=False, start_time=dtm.datetime(2025, 2, 21, 8, 0, 0), end_time=dtm.datetime(2025, 2, 22, 17, 20, 0))
    position_provider = ManualPositionProvider(
        [
            # StockPosition(asset_code="005930", asset_name="삼성전자", quantity=100, sell_possible_quantity=100, average_purchase_price=70000, current_price=70000, current_value=7000000, current_pnl=0, current_pnl_value=0)
        ]
    )
    broker = MockBroker(clock, position_provider, market="kr_stock", current_data_handling="virtual")
    # broker.create_order("005930", OrderSide.BUY, 100, OrderType.LIMIT, 70000)
    # broker.show_trading_history_report(make_file=True)
    # print(broker.get_minute_price("005930"))
    # print(broker.get_daily_price("005930", dtm.date(2025, 2, 13), dtm.date(2025, 2, 21)))
    # broker._get_minute_price_with_cache(dtm.date(2025, 2, 21), "005930")

    os.environ["TZ"] = "America/New_York"
    broker2 = MockBroker(clock, position_provider, market="us_stock", current_data_handling="virtual")
    # print(broker2.get_minute_price("AAPL"))
    # print(broker2.get_daily_price("AAPL", dtm.date(2025, 2, 13), dtm.date(2025, 2, 21)))
    # broker2._get_minute_price_with_cache(dtm.date(2025, 2, 21), "AAPL")
