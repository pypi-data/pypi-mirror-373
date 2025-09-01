import datetime
from typing import Dict, List, Optional, Union

import pandas as pd
import pytz

import pyqqq.config as c
from pyqqq.datatypes import DataExchange
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.array import chunk
from pyqqq.utils.local_cache import DiskCacheManager
from pyqqq.utils.logger import get_logger

logger = get_logger(__name__)
dailyCache = DiskCacheManager("daily_cache")


@dailyCache.memoize()
def get_all_ohlcv_for_date(
    date: datetime.date,
    adjusted: bool = True,
    exchange: Union[str, DataExchange] = "KRX",
) -> pd.DataFrame:
    """
    주어진 날짜에 대한 모든 주식의 OHLCV(Open, High, Low, Close, Volume) 데이터를 조회합니다.

    이 함수는 특정 날짜에 대한 모든 주식의 시가, 고가, 저가, 종가 및 거래량 데이터를 API를 통해 요청하고,
    이를 pandas DataFrame 형태로 반환합니다. 반환된 DataFrame은 'code'를 인덱스로 사용합니다.

    KRX: 2018년 1월 1일 데이터 부터 조회 가능합니다.
    NXT: 2025년 3월 4일 데이터 부터 조회 가능합니다.

    Args:
        date (datetime.date): 조회할 날짜.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX.

    Returns:
        pd.DataFrame: OHLCV 데이터를 포함하는 DataFrame. 'code' 컬럼은 DataFrame의 인덱스로 설정됩니다.

        DataFrame의 컬럼은 다음과 같습니다.

        - open (int): 시가.
        - high (int): 고가.
        - low (int): 저가.
        - close (int): 종가.
        - volume (int): 거래량.
        - value (int): 거래대금.

    Raises:
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> ohlcv_data = get_all_ohlcv_for_date(datetime.date(2025, 3, 4), exchange="KRX")
        >>> print(ohlcv_data)
                    open   high    low  close  volume        value
            code
            000020   6200   6220   6090   6130   41954    257785065
            000040    422    422    393    400  135979     54618038
            000050   6350   6350   6240   6290    9957     62588010
            000070  59800  61100  59500  60400   32555   1957081250
            000075  59000  59400  58300  59400    2600    151987900
            ...       ...    ...    ...    ...     ...          ...
            950160  35500  39150  35500  38950  332462  12638215825
            950170   4900   4955   4880   4900   24198    118688025
            950190   7860   7920   7770   7860   21309    166408215
            950200   3855   3855   3785   3800   23268     88458215
            950220    996    996    945    954  440017    421451605
    """
    if isinstance(date, datetime.datetime):
        date = date.date()

    exchange = DataExchange.validate(exchange)
    url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/daily/all/{date}"
    r = send_request(
        "GET",
        url,
        params={
            "adjusted": "true" if adjusted else "false",
            "current_date": datetime.date.today(),
            "exchange": exchange.value,
        },
    )
    raise_for_status(r)

    data = r.json()

    cols = data["cols"]
    rows = data["rows"]

    if not rows:
        return pd.DataFrame()
    else:
        df = pd.DataFrame(rows, columns=cols)

        # NOTE 서버 응답에서 diff, diff_rate 가 제거될 예정
        columns_to_drop = ["diff", "diff_rate", "date"]
        df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)
        df.set_index("code", inplace=True)

        df = df[["open", "high", "low", "close", "volume", "value"]]
        df = df.astype({"open": int, "high": int, "low": int, "close": int, "volume": int, "value": int})

        return df


def get_ohlcv_by_codes_for_period(
    codes: List[str],
    start_date: datetime.date,
    end_date: Optional[datetime.date] = None,
    adjusted: bool = True,
    ascending: bool = False,
    exchange: Union[str, DataExchange] = "KRX",
) -> Dict[str, pd.DataFrame]:
    """
    지정된 코드 리스트와 기간에 대한 OHLCV 데이터를 조회합니다.

    이 함수는 하나 이상의 주식 코드와 시작 날짜, 선택적으로 종료 날짜를 지정하여 해당 기간 동안의 OHLCV 데이터를 API를 통해 요청합니다.
    반환된 데이터는 각 주식 코드별로 시가, 고가, 저가, 종가, 거래량을 포함하는 pandas DataFrame 객체들로 구성된 딕셔너리 형태로 제공됩니다.
    각 DataFrame은 해당 주식의 날짜를 기반으로 역순으로 정렬됩니다.

    KRX: 2018년 1월 1일 데이터 부터 조회 가능합니다.
    NXT: 2025년 3월 4일 데이터 부터 조회 가능합니다.

    Args:
        codes (List[str]): 조회할 주식 코드들의 리스트.
        start_date (datetime.date): 조회할 기간의 시작 날짜.
        end_date (Optional[datetime.date]): 조회할 기간의 종료 날짜. 지정하지 않으면 최근 거래일 까지 조회됩니다.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        ascending (bool): 날짜 오름차순 여부. 기본값은 False.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX.

    Returns:
        dict: 주식 코드를 키로 하고, 해당 코드의 OHLCV 데이터를 포함하는 DataFrame을 값으로 하는 딕셔너리.

        DataFrame의 컬럼은 다음과 같습니다.

        - open (int): 시가.
        - high (int): 고가.
        - low (int): 저가.
        - close (int): 종가.
        - volume (int): 거래량.
        - value (int): 거래대금.

    Raises:
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> dfs = get_ohlcv_by_codes_for_period(['005930', '319640'], datetime.date(2025, 7, 28), datetime.date(2025, 7, 30))
        >>> print(dfs)
        {'319640':              open   high    low  close  volume      value
                    date
                    2025-07-30  20860  20930  20840  20870   47431  990834244
                    2025-07-29  20795  20850  20765  20810   39627  824529926
                    2025-07-28  20900  20985  20880  20965   26610  556764707,
        '005930':              open   high    low  close    volume          value
                    date
                    2025-07-30  71000  73700  70600  72600  34761444  2521446314798
                    2025-07-29  70800  70800  68800  70600  28190940  1977721049950
                    2025-07-28  68200  70400  67200  70400  35332500  2431396606750}
    """
    exchange = DataExchange.validate(exchange)
    tz = pytz.timezone("Asia/Seoul")
    chunks = chunk(codes, 20)
    result = {}

    for i, asset_codes in enumerate(chunks):
        url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/daily/series"
        params = {
            "codes": ",".join(asset_codes),
            "start_date": start_date,
            "adjusted": "true" if adjusted else "false",
            "current_date": datetime.date.today(),
            "exchange": exchange.value,
        }
        if end_date is not None:
            params["end_date"] = end_date

        r = send_request("GET", url, params=params)
        raise_for_status(r)

        data = r.json()
        cols = data["cols"]
        dataset = data["rows"]

        if not dataset:
            continue

        for code in dataset.keys():
            rows = dataset[code]
            for row in rows:
                dt = row[0]
                if dt[-1] == "Z":
                    dt = dt[:-1] + "+00:00"
                dt = datetime.datetime.fromisoformat(dt).astimezone(tz).replace(tzinfo=None)
                row[0] = dt

            rows.reverse()

            df = pd.DataFrame(rows, columns=cols)

            # NOTE 서버 응답에서 diff, diff_rate 가 제거될 예정
            columns_to_drop = ["diff", "diff_rate"]
            df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)
            df.set_index("date", inplace=True)

            df = df[["open", "high", "low", "close", "volume", "value"]]
            df = df.astype({"open": int, "high": int, "low": int, "close": int, "volume": int, "value": int})
            df.sort_index(ascending=ascending, inplace=True)
            result[code] = df

    return result
