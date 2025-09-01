from io import BytesIO
from pyqqq.utils.api_client import send_request
from pyqqq.utils.logger import get_logger
import datetime as dtm
import pandas as pd
import pyqqq.config as c

logger = get_logger(__name__)


def get_tick_data(date: dtm.date, asset_code: str) -> pd.DataFrame:
    """
    해당 일 체결 정보를 반환합니다

    Args:
        date (dtm.date): 조회할 날짜
        asset_code (str): 조회할 종목 코드

    Returns:
        pd.DataFrame: 요청한 일자의 해당 종목의 모든 체결 정보를 담은 DataFrame

        - chetime (datetime.time): 체결시간
        - sign (int): 전일대비구분 (1:상한 2:상승 3:보함 4:하한 5:하락)
        - change (int): 전일대비가격
        - drate (float): 등락율
        - price (int): 체결가
        - opentime (datetime.time): 시가시간
        - open (int): 시가
        - hightime (datetime.time): 고가시간
        - high (int): 고가
        - lowtime (datetime.time): 저가시간
        - low (int): 저가
        - cgubun (str): 체결구분 (-:매도 +:매수 NaN:동시호가)
        - cvolume (int): 체결량
        - volume (int): 누적거래량
        - value (int): 누적거래대금
        - mdvolume (int): 매도체결수량
        - msvolume (int): 매수체결수량
        - mdchecnt (int): 매도체결건수
        - mschecnt (int): 매수체결건수
        - cpower (float): 체결강도
        - w_avrg (int): 가중평균가
        - offerho (int): 매도호가
        - bidho (int): 매수호가
        - status (int): 장정보 (0:장중 10:장전시간외 4:장후시간외 3:장마감 47:시간외단일가)
        - jnilvolume (int): 전일거래량
        - shcode (str): 종목코드

    Examples:
        >>> df = get_tick_data(datetime.date.today() - datetime.timedelta(days=3), "017670")
        >>> print(df.head())
           mdchecnt  sign  mschecnt  mdvolume  w_avrg  cpower  offerho  cvolume  high  bidho  low  price cgubun  value  change  shcode   chetime opentime lowtime  volume  drate hightime  jnilvolume  msvolume  open  status
        0         1     3         0         1   37716    0.00        0        1     0      0    0  37715      -      0       0   69500  08:31:27      NaT     NaT       1    0.0      NaT           0         0     0      10
        1         2     3         0       352   37716    0.00        0      351     0      0    0  37715      -     13       0   69500  08:31:45      NaT     NaT     352    0.0      NaT           0         0     0      10
        2         2     3         1       352   37716    0.28        0        1     0      0    0  37715      +     13       0   69500  08:31:45      NaT     NaT     353    0.0      NaT           0         1     0      10
        3         2     3         2       352   37716    1.99        0        6     0      0    0  37715      +     14       0   69500  08:32:12      NaT     NaT     359    0.0      NaT           0         7     0      10
        4         2     3         3       352   37716   77.84        0      267     0      0    0  37715      +     24       0   69500  08:35:57      NaT     NaT     626    0.0      NaT           0       274     0      10

    """

    url = f"{c.PYQQQ_API_URL}/domestic-stock/daily/trades/{date}/{asset_code}"
    r = send_request(
        "GET",
        url,
    )
    if r.status_code != 200 and r.status_code != 201:
        logger.error(f"Failed to get tick data: {r.status_code}")
        return None

    with BytesIO() as byte_stream:
        byte_stream.write(r.content)
        byte_stream.seek(0)

        if date < dtm.date(2024, 4, 19):
            dtype = {"shcode": "str"}
            df = pd.read_csv(byte_stream, compression="xz", dtype=dtype)

            for col in ["chetime", "opentime", "hightime", "lowtime"]:
                df[col] = pd.to_datetime(df[col], format="%H%M%S").dt.time
        else:
            dtype = {"code": "str"}
            df = pd.read_csv(byte_stream, compression="xz", dtype=dtype)

            df["time"] = pd.to_datetime(df["time"], format="%H%M%S").dt.time

    return df
