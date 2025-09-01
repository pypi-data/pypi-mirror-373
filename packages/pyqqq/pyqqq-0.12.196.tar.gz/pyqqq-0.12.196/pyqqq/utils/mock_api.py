import os
import datetime
from functools import wraps
from decimal import Decimal
import pandas as pd

from pyqqq.datatypes import *


def with_mock():
    """
    Decorator for mocking api call
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if str(os.getenv('MOCKAPI')).lower() == 'true':
                    return mock_functions[func.__module__][func.__name__](*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except SkipMockGetException:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def skip_mock_get(func):
    """
    Decorator for skipping mock api call
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if str(os.getenv('MOCKAPI_SKIPGET')).lower() == 'true':
            raise SkipMockGetException()
        else:
            return func(*args, **kwargs)
    return wrapper


class SkipMockGetException(Exception):
    """
    Exception for skipping mock api call
    """


class MockEBestSimpleDomesticStock:
    @staticmethod
    @skip_mock_get
    def get_account(*args, **kwargs):
        return {'total_balance': 10000000, 'purchase_amount': 0, 'evaluated_amount': 0, 'pnl_amount': 10000000, 'pnl_rate': Decimal('0.000000')}

    @staticmethod
    @skip_mock_get
    def get_possible_quantity(*args, **kwargs):
        return {'investable_cash': 10000000, 'reusable_amount': 0, 'price': 70000, 'quantity': 142, 'amount': 9998000}

    @staticmethod
    @skip_mock_get
    def get_positions(*args, **kwargs):
        return []

    @staticmethod
    @skip_mock_get
    def get_historical_daily_data(*args, **kwargs):
        result = [
            {'date': datetime.date(2023, 3, 2), 'open': 60900, 'high': 61800, 'low': 60500, 'close': 60800, 'volume': 13049056},
            {'date': datetime.date(2023, 3, 3), 'open': 61000, 'high': 61200, 'low': 60500, 'close': 60500, 'volume': 10669655},
        ]
        df = pd.DataFrame(result)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        return df

    @staticmethod
    def create_order(*args, **kwargs):
        _arg_orders = ('self', 'asset_code', 'side', 'quantity', 'order_type', 'price')
        _args = {
            'asset_code': None,
            'side': None,
            'quantity': None,
            'order_type': OrderType.MARKET,
            'price': 0
        }
        for i, arg in enumerate(args):
            if i > 0:
                _args[_arg_orders[i]] = arg
        for k, v in kwargs.items():
            _args[k] = v

        def __get_ord_prc_ptn_code():
            order_type = _args['order_type']
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
            order_type = _args['order_type']
            if order_type in [OrderType.MARKET, OrderType.LIMIT]:
                return 0
            elif order_type in [OrderType.MARKET_IOC, OrderType.LIMIT_IOC]:
                return 1
            elif order_type in [OrderType.MARKET_FOK, OrderType.LIMIT_FOK]:
                return 2
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        def __get_bns_tp_code() -> int:
            side = _args['side']
            if side == OrderSide.BUY:
                return 2
            elif side == OrderSide.SELL:
                return 1
            else:
                raise ValueError("지원하지 않는 주문 방향입니다.")

        __get_bns_tp_code()
        __get_ord_prc_ptn_code()
        __get_ord_cndi_tp_code()

        return 'MockEBestOrdNo001'

    @staticmethod
    def update_order(*args, **kwargs):
        _arg_orders = ('self', 'org_order_no', 'asset_code', 'order_type', 'price', 'quantity')
        _args = {
            'org_order_no': None,
            'asset_code': None,
            'order_type': None,
            'price': None,
            'quantity': 0
        }
        for i, arg in enumerate(args):
            if i > 0:
                _args[_arg_orders[i]] = arg
        for k, v in kwargs.items():
            _args[k] = v

        def __get_ord_prc_ptn_code():
            order_type = _args['order_type']
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
            order_type = _args['order_type']
            if order_type in [OrderType.MARKET, OrderType.LIMIT]:
                return 0
            elif order_type in [OrderType.MARKET_IOC, OrderType.LIMIT_IOC]:
                return 1
            elif order_type in [OrderType.MARKET_FOK, OrderType.LIMIT_FOK]:
                return 2
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        __get_ord_prc_ptn_code()
        __get_ord_cndi_tp_code()

        return 'MockEBestOrdNo001'

    @staticmethod
    def cancel_order(*args, **kwargs):
        return 'MockEBestOrdNo001'


class MockKISSimpleDomesticStock:
    @staticmethod
    def create_order(*args, **kwargs):
        _arg_orders = ('self', 'asset_code', 'side', 'quantity', 'order_type', 'price')
        _args = {
            'asset_code': None,
            'side': None,
            'quantity': None,
            'order_type': OrderType.MARKET,
            'price': 0
        }
        for i, arg in enumerate(args):
            if i > 0:
                _args[_arg_orders[i]] = arg
        for k, v in kwargs.items():
            _args[k] = v

        def __get_order_type_code():
            order_type = _args['order_type']
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
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        def __get_order_side_code():
            side = _args['side']
            if side == OrderSide.BUY:
                return "buy"
            elif side == OrderSide.SELL:
                return "sell"
            else:
                raise ValueError("지원하지 않는 주문 방향입니다.")

        __get_order_side_code()
        __get_order_type_code()

        return 'MockKISOrdNo001'

    @staticmethod
    def update_order(*args, **kwargs):
        _arg_orders = ('self', 'org_order_no', 'order_type', 'price', 'quantity')
        _args = {
            'org_order_no': None,
            'order_type': None,
            'price': None,
            'quantity': 0
        }
        for i, arg in enumerate(args):
            if i > 0:
                _args[_arg_orders[i]] = arg
        for k, v in kwargs.items():
            _args[k] = v

        def __get_order_type_code():
            order_type = _args['order_type']
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
            else:
                raise ValueError("지원하지 않는 주문 유형입니다.")

        __get_order_type_code()

        return 'MockKISOrdNo001'

    @staticmethod
    def cancel_order(*args, **kwargs):
        return 'MockKISOrdNo001'


mock_functions = {
    'pyqqq.brokerage.ebest.simple': {
        'get_account': MockEBestSimpleDomesticStock.get_account,
        'get_possible_quantity': MockEBestSimpleDomesticStock.get_possible_quantity,
        'get_positions': MockEBestSimpleDomesticStock.get_positions,
        'get_historical_daily_data': MockEBestSimpleDomesticStock.get_historical_daily_data,
        'create_order': MockEBestSimpleDomesticStock.create_order,
        'update_order': MockEBestSimpleDomesticStock.update_order,
        'cancel_order': MockEBestSimpleDomesticStock.cancel_order,
    },
    'pyqqq.brokerage.kis.simple': {
        'create_order': MockKISSimpleDomesticStock.create_order,
        'update_order': MockKISSimpleDomesticStock.update_order,
        'cancel_order': MockKISSimpleDomesticStock.cancel_order,
    }
}
