from pyqqq.utils.api_client import raise_for_status, send_request
from typing import Union
import pandas as pd
import pyqqq.config as c


def get_ticker_info(symbol: str) -> Union[pd.DataFrame, None]:
    """
    종목 정보를 가져옵니다.

    Args:
        symbol (str): 종목 심볼 (ex. 'AAPL')

    Returns:
        pd.DataFrame: 종목 정보

        - exchange (str): 거래소 코드
        - order_symbol (str): 주문용 심볼
        - name (str): 종목명
        - kr_name (str): 한글 종목명
        - type (str): 종목 종류
        - reference_price (float): 기준가

    Examples:
        >>> df = get_ticker_info("AAPL")
        >>> print(df)
               exchange order_symbol       name kr_name   type  reference_price  bid_order_size  ask_order_size  tick_size
        symbol
        AAPL       NASD      NASAAPL  APPLE INC      애플  Stock           226.47               1               1          0
    """

    url = f"{c.PYQQQ_API_URL}/overseas-stock/tickers"
    params = {"symbol": symbol}

    r = send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

    return pd.DataFrame([r.json()]).set_index("symbol")
