import datetime
from typing import Dict, Union

import numpy as np
import pandas as pd
import pytz

import pyqqq.config as c
from pyqqq.datatypes import DataExchange
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.local_cache import DiskCacheManager
from pyqqq.utils.logger import get_logger

logger = get_logger(__name__)
minuteCache = DiskCacheManager("minute_cache")


@minuteCache.memoize()
def get_all_minute_data(
    time: datetime.datetime,
    source: str = "kis",
    adjusted: bool = True,
    exchange: Union[str, DataExchange] = "KRX",
) -> pd.DataFrame:
    """
    모든 종목의 분봉 데이터를 반환합니다.

    데이터 소스에 따라 데이터 조회 가능 시작일이 다릅니다. LS증권은 추후 제거될 예정입니다.

    데이터 소스별 조회 가능 기간:
        한국투자증권:
            - KRX: 2023년 7월 3일 데이터 부터 조회 가능합니다.
            - NXT: 2025년 3월 4일 데이터 부터 조회 가능합니다.

        LS증권(구 이베스트증권):
            - KRX: 2024년 4월 9일 ~ 2025년 7월 18일까지 데이터 조회 가능합니다.
            - NXT: 2025년 5월 12일 ~ 2025년 7월 18일까지 데이터 조회 가능합니다. 단, 30초 간격 데이터는 조회 불가능합니다.

    Args:
        time (datetime.datetime): 조회할 시간
        source (str): 데이터를 검색할 API. 'ebest' 또는 'kis'를 지정할 수 있습니다. 기본값은 'kis'입니다.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX.

    Returns:
        pd.DataFrame: 모든 종목의 분봉 데이터가 포함된 pandas DataFrame.

        DataFrame의 열은 다음과 같습니다:

        - time (datetime.datetime): 시간
        - open (int): 시가
        - high (int): 고가
        - low (int): 저가
        - close (int): 종가
        - volume (int): 거래량
        - value (int): 거래대금
        - cum_value (int): 누적거래대금
        - cum_volume (int): 누적거래량

    Raises:
        ValueError: 지원하지 않는 거래소 코드가 전달된 경우.

    Examples:
        >>> df = get_all_minute_data(datetime.datetime(2025, 8, 12, 15, 30), source="kis", exchange="UN")
        >>> print(df)
                time   open   high    low  close  volume     value  cum_volume   cum_value
        code
        000020 2025-08-12 15:30:00   6510   6510   6510   6510     356   2317560       33208   216896450
        000040 2025-08-12 15:30:00    586    586    586    586   34968  20491248     4617389  2743895196
        000050 2025-08-12 15:30:00   7290   7290   7290   7290     402   2930580       32918   241933340
        000070 2025-08-12 15:30:00  84400  84400  84400  84400     281  23716400       30040  2566753150
        000075 2025-08-12 15:30:00  83500  83500  83500  83500       0         0           0           0
        ...                    ...    ...    ...    ...    ...     ...       ...         ...         ...
        950170 2025-08-12 15:30:00   6310   6310   6310   6310     388   2448280      191052  1193696490
        950190 2025-08-12 15:30:00  10010  10010  10010  10010     257   2572570       18808   189271460
        950200 2025-08-12 15:30:00   3670   3670   3670   3670     101    370670        8521    31384290
        950210 2025-08-12 15:30:00  14170  14170  14170  14170    2732  38712440      153357  2203865640
        950220 2025-08-12 15:30:00   1193   1193   1193   1193    1335   1592655      829086  1005055869
    """
    tz = pytz.timezone("Asia/Seoul")
    exchange = DataExchange.validate(exchange)

    url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/minutes/all/{time.date()}/{time.strftime('%H%M')}"
    params = {
        "brokerage": source,
        "adjusted": "true" if adjusted else "false",
        "current_date": datetime.date.today(),
        "exchange": exchange.value,
    }

    r = send_request("GET", url, params=params)
    if r.status_code != 200 and r.status_code != 201:
        logger.error(f"Failed to get minute data: {r.text}")
        return

    rows = r.json()
    for data in rows:
        time = data["time"].replace("Z", "+00:00")
        time = datetime.datetime.fromisoformat(time).astimezone(tz).replace(tzinfo=None)
        data["time"] = time

    df = pd.DataFrame(rows)
    if not df.empty:
        dtypes = df.dtypes

        for k in [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "change",
            "totofferrem",
            "totbidrem",
        ]:
            if k in dtypes:
                dtypes[k] = np.dtype("int64")

        for k in ["diff", "chdegree"]:
            if k in dtypes:
                dtypes[k] = np.dtype("float64")

        if source == "kis":
            df = df[["code", "time", "open", "high", "low", "close", "volume", "value", "cum_volume", "cum_value"]]

        df = df.astype(dtypes)
        df.set_index("code", inplace=True)

    return df


@minuteCache.memoize()
def get_all_day_data(
    date: datetime.date,
    codes: list[str] | str,
    period: datetime.timedelta = datetime.timedelta(minutes=1),
    source: str = "kis",
    adjusted: bool = True,
    ascending: bool = True,
    exchange: Union[str, DataExchange] = "KRX",
) -> dict[str, pd.DataFrame] | pd.DataFrame:
    """
    지정된 날짜에 대해 하나 이상의 주식 코드에 대한 전체 분별 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 검색하여 반환합니다.

    데이터 소스에 따라 데이터 조회 가능 시작일이 다릅니다. LS증권은 추후 제거될 예정입니다.

    데이터 소스별 조회 가능 기간:
        한국투자증권:
            - KRX: 2023년 7월 3일 데이터 부터 조회 가능합니다.
            - NXT: 2025년 3월 4일 데이터 부터 조회 가능합니다.

        LS증권(구 이베스트증권):
            - KRX: 2024년 4월 26일 ~ 2025년 7월 17일까지 데이터 조회 가능합니다.
            - NXT: 조회 불가합니다.

    Args:
        date (datetime.date): 데이터를 검색할 날짜.
        codes (list[str]): 조회할 주식 코드들의 리스트. 최대 20개까지 지정할 수 있습니다.
        period (datetime.timedelta, optional): 반환된 데이터의 시간 간격. 기본값은 1분입니다. 30초 이상의 값을 30초간격으로 지정할 수 있습니다.
        source (str, optional): 데이터를 검색할 API. 'ebest' 또는 'kis'를 지정할 수 있습니다. 기본값은 'kis'입니다.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        ascending (bool): 오름차순 여부. 기본값은 True.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX. (cf. NXT의 경우 해당되지 않는 종목은 Empty DataFrame이 반환됩니다.)

    Returns:
        dict[str, pd.DataFrame]: 주식 코드를 키로 하고, 해당 주식의 일일 OHLCV 데이터가 포함된 pandas DataFrame을 값으로 하는 딕셔너리.
        각 DataFrame에는 변환된 'time' 열이 포함되어 있으며, 이는 조회된 데이터의 시간을 나타냅니다. 'time' 열은 DataFrame의 인덱스로 설정되고 오름차순으로 정렬됩니다.

        DataFrame의 열은 다음과 같습니다:

        - time (datetime.datetime): 시간
        - open (int): 시가
        - high (int): 고가
        - low (int): 저가
        - close (int): 종가
        - volume (int): 거래량
        - value (int): 거래대금
        - cum_volume (int): 누적거래량
        - cum_value (int): 누적거래대금

    Raises:
        requests.exceptions.RequestException: PYQQQ API로부터 데이터를 검색하는 과정에서 오류가 발생한 경우.

    Examples:
        >>> result = get_all_day_data(datetime.date(2025, 8, 12), codes=["005930", "319640"], source="kis", exchange="UN")
        >>> print(result["005930"])
                open   high    low  close  volume       value  cum_volume      cum_value
        time
        2025-08-12 08:00:00  71100  71300  71000  71200   39907  2840499700       39907     2840499700
        2025-08-12 08:01:00  71200  71200  71100  71200   17688  1258243300       57595     4098743000
        2025-08-12 08:02:00  71200  71300  71100  71300   37311  2656578100       94906     6755321100
        2025-08-12 08:03:00  71200  71300  71200  71300   12086   861096800      106992     7616417900
        2025-08-12 08:04:00  71300  71300  71200  71300   14868  1059991500      121860     8676409400
        ...                    ...    ...    ...    ...     ...         ...         ...            ...
        2025-08-12 19:56:00  71200  71300  71200  71300    3507   250012700    22367898  1603227575600
        2025-08-12 19:57:00  71200  71300  71200  71200    6834   487156900    22374732  1603714732500
        2025-08-12 19:58:00  71200  71300  71200  71300    9708   692159000    22384440  1604406891500
        2025-08-12 19:59:00  71300  71400  71200  71400   10540   751223500    22394980  1605158115000
        2025-08-12 20:00:00  71400  71400  71400  71400       0           0    22394980  1605158115000
    """
    assert isinstance(date, datetime.date), "date must be a datetime.date object"
    assert type(date) is datetime.date, "date must be a datetime.date object"
    assert isinstance(codes, list) or isinstance(codes, str), "codes must be a list of strings or single code"

    if isinstance(codes, list):
        assert all(isinstance(code, str) for code in codes), "codes must be a list of strings"
    assert len(codes) > 0, "codes must not be empty"
    assert len(codes) <= 20, "codes must not exceed 20"

    if period is not None:
        assert period >= datetime.timedelta(seconds=30), "period must be at least 30 seconds"
        assert period.total_seconds() % 30 == 0, "period must be a multiple of 30 seconds"

    tz = pytz.timezone("Asia/Seoul")
    target_codes = codes if isinstance(codes, list) else [codes]

    exchange = DataExchange.validate(exchange)

    if source == "ebest":
        url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/half-minutes/{date}"
    else:
        url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/minutes/{date}"

    r = send_request(
        "GET",
        url,
        params={
            "codes": ",".join(target_codes) if target_codes else None,
            "brokerage": source,
            "adjusted": "true" if adjusted else "false",
            "current_date": datetime.date.today(),
            "exchange": exchange.value,
        },
    )

    if r.status_code != 200 and r.status_code != 201:
        logger.error(f"Failed to get day data: {r.text}")
        r.raise_for_status()

    result = {}
    for code in target_codes:
        result[code] = pd.DataFrame()

    entries = r.json()
    cols = entries["cols"]
    if len(cols) == 0:
        return result

    time_index = cols.index("time")
    multirows = entries["rows"]

    for code in multirows.keys():
        rows = multirows[code]
        for row in rows:
            time = row[time_index].replace("Z", "+00:00")
            time = datetime.datetime.fromisoformat(time).astimezone(tz).replace(tzinfo=None)
            row[time_index] = time

        rows.reverse()

        df = pd.DataFrame(rows, columns=cols)

        if source == "kis":
            df = resample_kis_data(df, period)
        else:
            df = resample_ebest_data(df, period)

        df.sort_index(ascending=ascending, inplace=True)

        result[code] = df

    if isinstance(codes, str):
        return result[codes]
    else:
        return result


def resample_ebest_data(df, period):
    if period is not None and period.total_seconds() != 30:
        df["time"] = df["time"] - datetime.timedelta(seconds=30)
        df.set_index("time", inplace=True)

        minutes = period.total_seconds() / 60

        op_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "sign": "last",
            "change": "last",
            "diff": "last",
            "chdegree": "last",
            "mdvolume": "sum",
            "msvolume": "sum",
            "revolume": "sum",
            "mdchecnt": "sum",
            "mschecnt": "sum",
            "rechecnt": "sum",
            "cvolume": "sum",
            "mdchecnttm": "sum",
            "mschecnttm": "sum",
            "totofferrem": "last",
            "totbidrem": "last",
            "mdvolumetm": "sum",
            "msvolumetm": "sum",
        }

        df = df.resample(f"{minutes}min").apply(op_dict)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)

    dtypes = df.dtypes

    for k in [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "change",
        "totofferrem",
        "totbidrem",
    ]:
        dtypes[k] = np.dtype("int64")

    dtypes["diff"] = np.dtype("float64")
    dtypes["chdegree"] = np.dtype("float64")

    df = df.astype(dtypes)
    df.set_index("time", inplace=True)

    return df


def resample_kis_data(df, period):
    if period is not None and period.total_seconds() != 60:
        df.set_index("time", inplace=True)
        minutes = period.total_seconds() // 60

        op_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "value": "sum",
            "cum_volume": "sum",
            "cum_value": "sum",
        }

        df = df.resample(f"{minutes}min").apply(op_dict)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)

    dtypes = df.dtypes

    for k in [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "value",
        "cum_volume",
        "cum_value",
    ]:
        dtypes[k] = np.dtype("int64")

    df = df.astype(dtypes)
    df = df[["time", "open", "high", "low", "close", "volume", "value", "cum_volume", "cum_value"]]
    df.set_index("time", inplace=True)

    return df


def get_orderbook(code: str, time: datetime.datetime) -> Dict:
    """
    주식 종목의 주문 호가 정보를 반환합니다.

    Args:
        code (str): 종목 코드
        time (datetime.datetime): 조회할 시간

    Returns:
        dict: 호가 정보가 포함된 사전.
            - total_bid_volume (int): 총 매수 잔량.
            - total_ask_volume (int): 총 매도 잔량.
            - ask_price (int): 1차 매도 호가 가격.
            - ask_volume (int): 1차 매도 호가 잔량.
            - bid_price (int): 1차 매수 호가 가격.
            - bid_volume (int): 1차 매수 호가 잔량.
            - time (datetime.datetime): 현지 기준 호가 정보 조회 시간.
            - bids (list): 매수 호가 목록 (각 항목은 price와 volume을 포함하는 dict).
            - asks (list): 매도 호가 목록 (각 항목은 price과 volume을 포함하는 dict).
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/orderbook/minutes/{code}/{time.date()}/{time.strftime('%H%M')}"
    r = send_request("GET", url)

    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

    data = r.json()
    data.pop("code")
    data["time"] = datetime.datetime.fromisoformat(data["time"]).astimezone(pytz.timezone("Asia/Seoul")).replace(tzinfo=None)

    return data
