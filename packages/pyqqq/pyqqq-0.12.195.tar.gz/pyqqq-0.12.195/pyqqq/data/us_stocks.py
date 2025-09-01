from typing import Dict, List, Union
from pyqqq.utils.logger import get_logger
from pyqqq.utils.api_client import raise_for_status, send_request
import pandas as pd
import datetime as dtm
import pyqqq.config as c
from io import StringIO

logger = get_logger(__name__)


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


def get_ohlcv_by_codes_for_period(
    tickers: List[str] | str,
    start_date: dtm.date,
    end_date: dtm.date,
    ascending: bool = True,
    adjusted: bool = True,
) -> Dict[str, pd.DataFrame] | pd.DataFrame:
    """
    지정된 티커와 기간에 대한 미국 주식의 OHLCV 데이터를 조회합니다.

    이 함수는 하나 이상의 티커와 시작 날짜, 종료 날짜를 지정하여 해당 기간 동안의 OHLCV 데이터를 API를 통해 요청합니다.
    단일 티커를 문자열로 전달하면 해당 티커의 DataFrame을 반환하고,
    티커 리스트를 전달하면 각 티커별로 DataFrame을 포함하는 딕셔너리를 반환합니다.

    Args:
        tickers (Union[List[str], str]): 조회할 티커 또는 티커들의 리스트.
        start_date (dtm.date): 조회할 기간의 시작 날짜.
        end_date (dtm.date): 조회할 기간의 종료 날짜.
        ascending (bool): 날짜 오름차순 여부. 기본값은 True.
        adjusted (bool): 수정 주가 여부. 기본값은 True.

    Returns:
        Union[Dict[str, pd.DataFrame], pd.DataFrame]:
        - 단일 티커 입력시: 해당 티커의 OHLCV 데이터를 포함하는 DataFrame
        - 티커 리스트 입력시: 티커를 키로 하고, 해당 티커의 OHLCV 데이터를 포함하는 DataFrame을 값으로 하는 딕셔너리

        DataFrame의 컬럼은 다음과 같습니다:

        - open (float): 시가
        - high (float): 고가
        - low (float): 저가
        - close (float): 종가
        - volume (int): 거래량

    Raises:
        HTTPError: API 요청이 실패했을 때 발생

    Examples:
        >>> # 단일 티커 조회
        >>> df = get_ohlcv_by_codes_for_period('AAPL', dtm.date(2024, 5, 7), dtm.date(2024, 5, 9))
        >>> print(df)
                    open    high     low   close    volume
        date
        2024-05-07  173.5  174.2   172.3  173.8  55234123
        2024-05-08  173.9  174.8   173.1  174.2  48521234
        2024-05-09  174.3  175.1   173.8  174.9  52145678

        >>> # 복수 티커 조회
        >>> dfs = get_ohlcv_by_codes_for_period(['AAPL', 'MSFT'], dtm.date(2024, 5, 7), dtm.date(2024, 5, 9))
        >>> print(dfs['AAPL'])
                    open    high     low   close    volume
        date
        2024-05-07  173.5  174.2   172.3  173.8  55234123
        2024-05-08  173.9  174.8   173.1  174.2  48521234
        2024-05-09  174.3  175.1   173.8  174.9  52145678
    """
    if isinstance(tickers, str):
        df = _get_daily_ohlcv(tickers, start_date, end_date, adjusted)
        if not ascending:
            df = df.iloc[::-1]
        return df

    else:
        dfs = {}
        for ticker in tickers:
            df = _get_daily_ohlcv(ticker, start_date, end_date, adjusted)
            if not ascending:
                df = df.iloc[::-1]
            dfs[ticker] = df
        return dfs


def _get_daily_ohlcv(ticker: str, start_date: dtm.date, end_date: dtm.date, adjusted: bool = True) -> pd.DataFrame:
    url = f"{c.PYQQQ_API_URL}/overseas-stock/ohlcv/daily"
    params = {
        "ticker": ticker,
        "fromDate": start_date.strftime("%Y-%m-%d"),
        "toDate": end_date.strftime("%Y-%m-%d"),
        "adjusted": "true" if adjusted else "false",
    }
    r = send_request("GET", url, params=params)
    raise_for_status(r)

    if r.text == "":
        df = pd.DataFrame([], columns=["open", "high", "low", "close", "volume"])
        df.index.name = "date"
        return df

    df = pd.read_csv(StringIO(r.text))
    df["time"] = pd.to_datetime(df["time"])
    df["time"] = df["time"].dt.tz_convert("America/New_York")
    df["date"] = df["time"].dt.date
    df = df[["date", "open", "high", "low", "close", "volume"]]
    df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": int})
    df.set_index("date", inplace=True)

    return df


def get_all_ohlcv_for_date(date: dtm.date) -> pd.DataFrame:
    """
    주어진 날짜에 대한 모든 미국 주식의 OHLCV(Open, High, Low, Close, Volume) 데이터를 조회합니다.

    이 함수는 특정 날짜에 대한 모든 미국 주식의 시가, 고가, 저가, 종가 및 거래량 데이터를 API를 통해 요청하고,
    이를 pandas DataFrame 형태로 반환합니다. 반환된 DataFrame은 'ticker'를 인덱스로 사용합니다.

    Args:
        date (dtm.date): 조회할 날짜.

    Returns:
        pd.DataFrame: OHLCV 데이터를 포함하는 DataFrame. 'ticker' 컬럼은 DataFrame의 인덱스로 설정됩니다.

        DataFrame의 컬럼은 다음과 같습니다:

        - open (float): 시가
        - high (float): 고가
        - low (float): 저가
        - close (float): 종가
        - volume (int): 거래량

    Raises:
        HTTPError: API 요청이 실패했을 때 발생

    Examples:
        >>> ohlcv_data = get_all_ohlcv_for_date(dtm.date(2024, 5, 8))
        >>> print(ohlcv_data)
                open    high     low   close     volume
        ticker
        AAPL    173.9  174.8   173.1  174.2  48521234
        MSFT    419.2  420.7   416.3  418.5  22145678
        GOOGL   142.5  143.8   141.9  143.2  15234567
        AMZN    178.2  179.5   177.4  178.8  32456789
        META    435.1  437.2   433.6  436.4  18234567
        ...
    """
    url = f"{c.PYQQQ_API_URL}/overseas-stock/ohlcv/daily/all"
    params = {
        "date": date.strftime("%Y-%m-%d"),
    }
    r = send_request("GET", url, params=params)
    raise_for_status(r)

    if r.text == "":
        df = pd.DataFrame([], columns=["open", "high", "low", "close", "volume"])
        df.index.name = "ticker"

        return df

    df = pd.read_csv(StringIO(r.text))
    df = df[["ticker", "open", "high", "low", "close", "volume"]]
    df.set_index("ticker", inplace=True)

    return df


def get_all_day_data(date: dtm.date, tickers: List[str] | str, ascending: bool = True) -> pd.DataFrame | Dict[str, pd.DataFrame]:
    """
    주어진 날짜의 미국 주식 분봉 OHLCV 데이터를 조회합니다.

    이 함수는 특정 날짜에 대한 미국 주식의 1분 단위 시가, 고가, 저가, 종가 및 거래량 데이터를 API를 통해 요청합니다.
    단일 티커를 문자열로 전달하면 해당 티커의 DataFrame을 반환하고,
    티커 리스트를 전달하면 각 티커별로 DataFrame을 포함하는 딕셔너리를 반환합니다.

    Args:
        date (dtm.date): 조회할 날짜
        tickers (Union[List[str], str]): 조회할 티커 또는 티커들의 리스트
        ascending (bool): 시간 오름차순 여부. 기본값은 True

    Returns:
        Union[pd.DataFrame, Dict[str, pd.DataFrame]]:

        - 단일 티커 입력시: 해당 티커의 분봉 OHLCV 데이터를 포함하는 DataFrame
        - 티커 리스트 입력시: 티커를 키로 하고, 해당 티커의 분봉 OHLCV 데이터를 포함하는 DataFrame을 값으로 하는 딕셔너리

        DataFrame의 인덱스는 뉴욕 시간대의 datetime이며, 컬럼은 다음과 같습니다:

        - open (float): 시가
        - high (float): 고가
        - low (float): 저가
        - close (float): 종가
        - volume (int): 거래량

    Raises:
        HTTPError: API 요청이 실패했을 때 발생

    Examples:
        >>> # 단일 티커 조회
        >>> df = get_all_day_data(dtm.date(2024, 5, 8), 'AAPL')
        >>> print(df)
                                    open    high     low   close  volume
        time(America/New_York)
        2024-05-08 09:30:00      173.90  174.15  173.85  174.00   52345
        2024-05-08 09:31:00      174.00  174.12  173.95  174.05   48123
        2024-05-08 09:32:00      174.05  174.20  174.00  174.15   45678
        ...

        >>> # 복수 티커 조회
        >>> dfs = get_all_day_data(dtm.date(2024, 5, 8), ['AAPL', 'MSFT'])
        >>> print(dfs['AAPL'])
                                    open    high     low   close  volume
        time(America/New_York)
        2024-05-08 09:30:00      173.90  174.15  173.85  174.00   52345
        2024-05-08 09:31:00      174.00  174.12  173.95  174.05   48123
        2024-05-08 09:32:00      174.05  174.20  174.00  174.15   45678
        ...
    """
    if isinstance(tickers, str):
        df = _get_minute_ohlcv(tickers, date)
        if not ascending:
            df = df.iloc[::-1]
        return df
    else:
        dfs = {}
        for ticker in tickers:
            df = _get_minute_ohlcv(ticker, date)
            if not ascending:
                df = df.iloc[::-1]
            dfs[ticker] = df
        return dfs


def _get_minute_ohlcv(ticker: str, date: dtm.date) -> pd.DataFrame:
    url = f"{c.PYQQQ_API_URL}/overseas-stock/ohlcv/minutes"
    params = {
        "ticker": ticker,
        "date": date.strftime("%Y-%m-%d"),
    }
    r = send_request("GET", url, params=params)
    raise_for_status(r)

    if r.text == "":
        df = pd.DataFrame([], columns=["open", "high", "low", "close", "volume", "value", "cum_volume", "cum_value"])
        df.index.name = "time"
        return df

    df = pd.read_csv(StringIO(r.text))
    df["time"] = pd.to_datetime(df["time"])
    df["time"] = df["time"].dt.tz_convert("America/New_York")

    columns = ["time", "open", "high", "low", "close", "volume"]
    for col in ["value", "cum_volume", "cum_value"]:
        if col in df.columns:
            columns.append(col)

    df = df[columns]
    df.set_index("time", inplace=True)

    return df


def get_all_minute_data(time: dtm.datetime) -> pd.DataFrame:
    """
    주어진 시간에 대한 모든 미국 주식의 분봉 OHLCV 데이터를 조회합니다.

    이 함수는 특정 시간에 대한 모든 미국 주식의 시가, 고가, 저가, 종가 및 거래량 데이터를 API를 통해 요청하고,
    이를 pandas DataFrame 형태로 반환합니다. 반환된 DataFrame은 'ticker'를 인덱스로 사용합니다.

    Args:
        time (dtm.datetime): 조회할 시간. 뉴욕 시간대(America/New_York) 기준으로 처리됩니다.

    Returns:
        pd.DataFrame: 모든 미국 주식의 분봉 OHLCV 데이터를 포함하는 DataFrame. 'ticker' 컬럼은 DataFrame의 인덱스로 설정됩니다.

        DataFrame의 컬럼은 다음과 같습니다:

        - open (float): 시가
        - high (float): 고가
        - low (float): 저가
        - close (float): 종가
        - volume (int): 거래량

    Raises:
        HTTPError: API 요청이 실패했을 때 발생

    Examples:
        >>> minute_data = get_all_minute_data(dtm.datetime(2024, 5, 8, 9, 30, tzinfo=ZoneInfo("America/New_York")))
        >>> print(minute_data)
                open    high     low   close   volume
        ticker
        AAPL   173.90  174.15  173.85  174.00   52345
        MSFT   419.20  419.80  419.00  419.50   25678
        GOOGL  142.50  142.80  142.30  142.60   18234
        AMZN   178.20  178.50  178.00  178.30   42567
        META   435.10  435.60  434.80  435.20   15678
        ...
    """
    url = f"{c.PYQQQ_API_URL}/overseas-stock/ohlcv/minutes/all"
    params = {
        "time": time.isoformat(),
    }
    r = send_request("GET", url, params=params)
    raise_for_status(r)

    if r.text == "":
        df = pd.DataFrame([], columns=["open", "high", "low", "close", "volume"])
        df.index.name = "ticker"
        return df

    df = pd.read_csv(StringIO(r.text))
    df = df[["ticker", "open", "high", "low", "close", "volume"]]
    df.set_index("ticker", inplace=True)

    return df
