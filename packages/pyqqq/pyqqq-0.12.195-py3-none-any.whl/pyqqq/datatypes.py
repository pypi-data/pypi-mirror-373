from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from typing import Optional, Union
import datetime


class Exchange(Enum):
    KRX = "KRX"
    """ 한국거래소 """
    NXT = "NXT"
    """ 넥스트레이드 """
    NYSE = "NYSE"
    """ 뉴욕거래소 """


class DataExchange(Enum):
    KRX = "KRX"
    """ 한국거래소 """
    NXT = "NXT"
    """ 넥스트레이드 """
    UN = "UN"
    """ 통합 """

    @classmethod
    def validate(cls, exchange: Union[str, "DataExchange"]) -> "DataExchange":
        if isinstance(exchange, cls):
            return exchange
        if isinstance(exchange, str):
            try:
                return cls(exchange)
            except ValueError:
                raise ValueError(f"지원하지 않는 거래소 코드입니다: {exchange}")

        raise TypeError(f"exchange는 str 또는 DataExchange 타입이어야 합니다. 현재 타입: {type(exchange)}")


class OrderExchange(Enum):
    KRX = 1
    """ 한국거래소 """
    NXT = 2
    """ 넥스트레이드 """
    SOR = 3
    """ 자동주문전송 """


class OrderSide(Enum):
    SELL = 1
    """ 매도 """
    BUY = 2
    """ 매수 """


class OrderType(Enum):
    LIMIT = 0
    """ 지정가 """
    LIMIT_IOC = 11
    """ 지정가, 즉시(일부)체결 그리고 잔량취소 """
    LIMIT_FOK = 12
    """ 지정가, 즉시 전량 체결 또는 전량취소 """
    LIMIT_CONDITIONAL = 2
    """ 조건부지정가, 지정가 주문을 넣고 장 마감까지 체결되지 않은 경우 동시호가 가격으로 체결 시킴 """
    MARKET = 1
    """ 시장가 """
    MARKET_IOC = 13
    """ 시장가, 즉시 (일부)체결 그리고 잔량취소 """
    MARKET_FOK = 14
    """ 시장가, 즉시 전량체결 또는 전량취소 """
    PRIMARY_PRICE = 3
    """ 최우선지정가, 반대방향의 1차호가로 주문 제출 """
    BEST_PRICE = 4
    """ 최유리지정가, 같은방향의 1차호가로 주문 제출 """
    BEST_PRICE_IOC = 15
    """ 최유리지정가, 즉시 (일부)체결 그리고 잔량취소"""
    BEST_PRICE_FOK = 16
    """ 최유리지정가, 즉시 전량체결 또는 전량취소"""
    PRE_MARKET = 5
    """ 장전단일가, 장전 단일가 주문 """
    AFTER_MARKET = 6
    """ 시간외종가, 시간외 종가 주문 """
    AFTER_MARKET_SINGLE_PRICE = 7
    """ 시간외단일가, 시간외 단일가 주문 """
    SELF_STOCK = 8
    """ 자사주, 자사주 매수 또는 매도 주문 """
    SELF_STOCK_S_OPTION = 9
    """ 자사주 S옵션, 자사주 매수 또는 매도 주문 """
    SELF_STOCK_MONETARY_TRUST = 10
    """ 자기주식금융신탁 """
    MOO = 31
    """ Market On Open, 해외 주식 주문 유형 (매도시에만 가능)"""
    LOO = 32
    """ Limit On Open, 해외 주식 주문 유형 """
    MOC = 33
    """ Market On Close, 해외 주식 주문 유형 (매도시에만 가능) """
    LOC = 34
    """ Limit On Close, 해외 주식 주문 유형 """
    MID_POINT = 21
    """ 중간가 """
    MID_POINT_IOC = 23
    """ 중간가, 즉시 (일부)체결 그리고 잔량취소 """
    MID_POINT_FOK = 24
    """ 중간가, 즉시 전량체결 또는 전량취소 """
    STOP_LIMIT = 22
    """ 스톱 지정가 """


class OrderRequestType(Enum):
    NEW = 1
    """ 신규주문 """
    MODIFY = 2
    """ 주문수정 """
    CANCEL = 3
    """ 주문취소 """


class TransactionStatus(Enum):
    ORDER = 1
    """ 주문 """
    EXECUTION = 2
    """ 체결 """


@dataclass
class StockPosition:
    """
    주식 보유 종목 정보를 담는 데이터 클래스입니다.
    """

    asset_code: str
    """ 종목 코드 """
    asset_name: str
    """ 종목 이름 """
    quantity: int
    """ 보유 수량 """
    sell_possible_quantity: int
    """ 매도 가능 수량 """
    average_purchase_price: Decimal
    """ 평균 매입 가격 """
    current_price: Optional[int | Decimal] = None
    """ 현재 가격 """
    current_value: Optional[int | Decimal] = None
    """ 현재 가치 """
    current_pnl: Optional[Decimal] = None
    """ 현재 손익률 """
    current_pnl_value: Optional[int | Decimal] = None
    """ 현재 손익 금액 """


@dataclass(kw_only=True)
class OverseasStockPosition(StockPosition):
    """
    해외 주식 보유 종목 정보를 담는 데이터 클래스입니다.
    """

    exchange: str
    """ 거래소 """
    currency: str
    """ 통화 """


@dataclass
class StockOrder:
    """
    주식 주문 정보를 담는 데이터 클래스입니다.
    """

    order_no: str
    """ 주문 번호 """
    asset_code: str
    """ 종목 코드 """
    side: OrderSide
    """ 주문 방향 """
    price: int | Decimal
    """ 주문 가격 """
    quantity: int
    """ 주문 수량 """
    filled_quantity: int
    """ 체결 수량 """
    pending_quantity: int
    """ 미체결 수량 """
    order_time: datetime.datetime
    """ 주문 시각 """
    filled_price: Optional[int | Decimal] = None
    """ 체결 가격 """
    current_price: Optional[int | Decimal] = None
    """ 현재 가격 """
    is_pending: Optional[bool] = None
    """ 미체결 여부 """
    org_order_no: Optional[str] = None
    """ 원주문번호 """
    order_type: Optional[OrderType] = None
    """ 주문 유형 """
    req_type: Optional[OrderRequestType] = None
    """ 주문 요청 유형 """
    exchange: Optional[OrderExchange] = None
    """ 거래소 """


@dataclass(kw_only=True)
class OverseasStockOrder(StockOrder):
    """
    해외 주식 주문 정보를 담는 데이터 클래스입니다.
    """

    exchange: str
    """ 거래소 """
    currency: str
    """ 통화 """
    reject_reason: Optional[str] = None
    """ 거부 사유 """
    order_kr_time: Optional[datetime.datetime] = None
    """ 한국 기준 주문 시각 """


@dataclass
class OrderEvent:
    asset_code: str
    """ 종목 코드 """
    order_no: str
    """ 주문 번호 """
    side: OrderSide
    """ 매도 / 매수 """
    order_type: OrderType
    """ 주문 유형 """
    quantity: int
    """ 주문 수량 """
    price: int
    """ 주문 가격 """
    event_type: str
    """ 이벤트 유형 - accepted, executed, cancelled, rejected """
    account_no: Optional[str] = None
    """ 계좌 번호 """
    filled_quantity: Optional[int] = None
    """ 체결 수량 """
    filled_price: Optional[int] = None
    """ 체결 가격 """
    filled_time: Optional[datetime.datetime] = None
    """ 체결 시각 """
    org_order_no: Optional[str] = None
    """ 원주문번호 """
    average_purchase_price: Optional[Decimal] = None
    """ 평균 매입 가격 """
    exchange: Optional[OrderExchange] = None
    """ 거래소 """

    @staticmethod
    def with_pending_order(account_no: str, order: StockOrder):
        """
        미체결 주문 정보로 이벤트 생성

        Args:
            account_no (str): 계좌 번호
            order (StockOrder): 주문 정보
        """
        return OrderEvent(
            asset_code=order.asset_code,
            order_no=order.order_no,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
            status="accepted",
            account_no=account_no,
            filled_quantity=order.filled_quantity,
            filled_price=order.filled_price,
            filled_time=None,
            org_order_no=order.org_order_no,
            exchange=order.exchange,
        )


@dataclass
class TradingHistory:
    """거래내역 정보를 담는 데이터 클래스입니다"""

    date: str
    """ 거래일자 (YYYYMMDD) """
    order_no: str
    """ 주문번호 """
    side: str
    """ 매도:sell / 매수:buy """
    asset_code: str
    """ 종목코드 """
    quantity: int
    """ 수량 """
    filled_price: int
    """ 체결가격 """
    average_purchase_price: Optional[float] = None
    """ 평균 매입가 """
    tax: Optional[float] = None
    """ 제세금 (증권거래세+지방소득세) """
    fee: Optional[float] = None
    """ 수수료 """
    pnl: Optional[float] = None
    """ 손익금액 """
    pnl_rate: Optional[float] = None
    """ 손익률 """
    executed_time: Optional[int] = None
    """ 체결시간 """
    partial: Optional[bool] = None
    """ 일부체결 여부 """
