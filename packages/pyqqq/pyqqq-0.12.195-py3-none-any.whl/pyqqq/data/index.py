from typing import Dict, List, Optional
from pyqqq.utils.array import chunk
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.local_cache import DiskCacheManager
from pyqqq.utils.logger import get_logger
import datetime as dtm
import pandas as pd
import pyqqq.config as c

logger = get_logger(__name__)
indexCache = DiskCacheManager("index_cache")


@indexCache.memoize()
def get_index_ohlcv_for_date(date: dtm.date) -> pd.DataFrame:
    """
    주어진 날짜에 대한 모든 지수의 OHLCV(Open, High, Low, Close, Volume) 데이터를 조회합니다.

    이 함수는 특정 날짜에 대한 모든 지수의 시가, 고가, 저가, 종가 및 거래량 데이터를 API를 통해 요청하고,
    이를 pandas DataFrame 형태로 반환합니다. 반환된 DataFrame은 'name'를 인덱스로 사용합니다.

    2018년 1월 1일 데이터 부터 조회 가능합니다.

    Args:
        date (dtm.date): 조회할 날짜.

    Returns:
        pd.DataFrame: OHLCV 데이터를 포함하는 DataFrame. 'name' 컬럼은 DataFrame의 인덱스로 설정됩니다.

        DataFrame의 컬럼은 다음과 같습니다.

        - open (float): 시가.
        - high (float): 고가.
        - low (float): 저가.
        - close (float): 종가.
        - volume (int): 거래량.
        - value (int): 거래대금.
        - diff (float): 종가 대비 전일 종가의 차이.
        - diff_rate (float): 종가 대비 전일 종가의 변화율.

    Raises:
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> ohlcv_data = get_index_ohlcv_for_date(dtm.date(2018, 1, 2))
        >>> print(ohlcv_data)
                    open     high      low    close  volume    value   diff  diff_rate
            name
            KOSPI   2474.86  2481.02  2465.94  2479.65  262205  4786386  12.16       0.49
            KOSDAQ   803.63   813.40   800.54   812.45  989204  6648960  14.03       1.76
            ...
    """

    url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/index/all/{date}"
    r = send_request("GET", url)
    raise_for_status(r)

    data = r.json()

    cols = data["cols"]
    rows = data["rows"]

    if not rows:
        return pd.DataFrame()
    else:
        df = pd.DataFrame(rows, columns=cols)
        df.drop(columns=["date"], inplace=True)
        df = df[["name", "open", "high", "low", "close", "volume", "value", "change", "change_percent"]]
        df.rename(columns={"change": "diff", "change_percent": "diff_rate"}, inplace=True)
        df.set_index("name", inplace=True)

        return df


def get_ohlcv_by_indices_for_period(
    indices: List[str],
    start_date: dtm.date,
    end_date: Optional[dtm.date] = None,
) -> Dict[str, pd.DataFrame]:
    """
    지정된 지수 리스트와 기간에 대한 OHLCV 데이터를 조회합니다.

    이 함수는 하나 이상의 지수와 시작 날짜, 선택적으로 종료 날짜를 지정하여 해당 기간 동안의 OHLCV 데이터를 API를 통해 요청합니다.
    반환된 데이터는 각 주식 지수별로 시가, 고가, 저가, 종가, 거래량을 포함하는 pandas DataFrame 객체들로 구성된 딕셔너리 형태로 제공됩니다.
    각 DataFrame은 해당 지수의 날짜를 기반으로 역순으로 정렬됩니다.

    2018년 1월 1일 데이터 부터 조회 가능합니다. 당일 실시간 조회는 지원하지 않습니다.

    Args:
        indices (List[str]): 조회할 지수 리스트.
        start_date (dtm.date): 조회할 기간의 시작 날짜.
        end_date (Optional[dtm.date]): 조회할 기간의 종료 날짜. 지정하지 않으면 최근 거래일 까지 조회됩니다.

    Returns:
        dict: 지수명을 키로 하고, 해당 지수의 OHLCV 데이터를 포함하는 DataFrame을 값으로 하는 딕셔너리.

        DataFrame의 컬럼은 다음과 같습니다.

        - open (float): 시가.
        - high (float): 고가.
        - low (float): 저가.
        - close (float): 종가.
        - volume (int): 거래량.
        - value (int): 거래대금.
        - diff (float): 종가 대비 전일 종가의 차이.
        - diff_rate (float): 종가 대비 전일 종가의 변화율.

    Raises:
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> dfs = get_ohlcv_by_indices_for_period(['KOSPI', 'KOSDAQ'], dtm.date(2024, 5, 7), dtm.date(2024, 5, 9))
        >>> print(dfs)
        {'KOSPI':                open     high      low    close  volume    value   diff  diff_rate
                    date
                    2018-01-05  2476.85  2497.52  2475.51  2497.52  308770  6317518  31.06       1.26
                    2018-01-04  2502.50  2502.50  2466.45  2466.46  333836  6896287 -19.89      -0.80
                    2018-01-03  2484.63  2493.40  2481.91  2486.35  331095  6019622   6.70       0.27
                    2018-01-02  2474.86  2481.02  2465.94  2479.65  262205  4786386  12.16       0.49,
        'KOSDAQ':               open    high     low   close   volume    value   diff  diff_rate
                    date
                    2018-01-05  812.05  828.04  812.05  828.03  1229153  7724099  20.02       2.48
                    2018-01-04  825.11  825.57  802.83  808.01  1346454  8340291 -14.30      -1.74
                    2018-01-03  816.30  824.18  812.22  822.31  1203096  8157560   9.86       1.21
                    2018-01-02  803.63  813.40  800.54  812.45   989204  6648960  14.03       1.76}

    """

    for market in indices:
        assert market in ["KOSPI", "KOSDAQ"], "indices는 'KOSPI' 또는 'KOSDAQ' 만 허용합니다."

    # NOTE KOSPI200 등 추가 지수를 대비하여 chunk 코드 남김
    chunks = chunk(indices, 20)
    result = {}

    for i, asset_indices in enumerate(chunks):
        url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/index/series"
        params = {
            "indices": ",".join(asset_indices),
            "start_date": start_date,
        }
        if end_date is not None:
            params["end_date"] = end_date

        r = send_request("GET", url, params=params)
        raise_for_status(r)

        data = r.json()
        cols = data["cols"]
        dataset = data["rows"]

        indices_df = pd.DataFrame(dataset, columns=cols)
        if indices_df.empty:
            return indices_df

        indices_df["date"] = indices_df["date"].apply(lambda dt: pd.to_datetime(dt))
        indices_df = indices_df[["name", "date", "open", "high", "low", "close", "volume", "value", "change", "change_percent"]]
        indices_df.rename(columns={"change": "diff", "change_percent": "diff_rate"}, inplace=True)

        for index in indices:
            df = indices_df[indices_df["name"] == index].copy()
            df = df.drop(columns=["name"])
            df.set_index("date", inplace=True)
            df.sort_index(ascending=False, inplace=True)
            result[index] = df

    return result
