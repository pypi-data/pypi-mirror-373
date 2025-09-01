import datetime as dtm
from typing import List, Optional, Union

import numpy as np
import pandas as pd

import pyqqq.config as c
from pyqqq.datatypes import DataExchange
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.array import chunk
from pyqqq.utils.compute import get_krx_tick_size, quantize_adjusted_price
from pyqqq.utils.local_cache import DiskCacheManager
from pyqqq.utils.market_schedule import get_last_trading_day, get_market_schedule

domesticCache = DiskCacheManager("domestic_cache")


def get_alert_stocks(alert_type: str, date: dtm.date = None) -> Optional[pd.DataFrame]:
    """
    시장 경보 종목을 조회합니다.

    2024년 3월 25일 데이터 부터 조회 가능합니다.

    Args:
        alert_type (str): 경보종류. caution:투자주의종목 warning:투자경고종목 risk:투자위험종목
        date (dtm.date, optional): 조회할 날짜. 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame|None: 경보 종목 리스트. 해당일에 저장된 데이터가 없으면 None, 저장되었지만 지정 종목이 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - name (str): 종목명
        - current_price (int): 현재가
        - change (int): 전일대비가격
        - change_rate (float): 전일대비등락율
        - volume (int): 거래량
        - bid_price (int): 매수호가
        - ask_price (int): 매도호가
        - per (float): PER

    Examples:
        >>> df = get_alert_stocks('caution')
        >>> print(df.head())
                    name  current_price  change  change_rate   volume  bid_price  ask_price    per
        code
        402340   SK스퀘어          77600    2400        -3.00   303590      77000      76900  -8.49
        053950    경남제약           1570       1         0.06  4857452       1569       1568  -4.91
        012320  경동인베스트         113100   11800        11.65   994188     118800     118700  22.05
        002720    국제약품           6820     310        -4.35  5559738       6900       6890 -17.14
        219420  링크제니시스           9100     160         1.79  1720993       9120       9100  83.49
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/alert-stocks/{alert_type}"
    params = {}
    if date:
        params["date"] = date

    r = send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

        df = pd.DataFrame(r.json())
        if not df.empty:
            df.set_index("code", inplace=True)
        return df


def get_invest_alert_stocks(alert_type: str, date: dtm.date = None) -> Optional[pd.DataFrame]:
    """
    시장 경보 종목을 조회합니다.

    2018년 1월 1일 데이터 부터 조회 가능합니다.

    Args:
        alert_type (str): 경보종류. caution:투자주의종목 alert:투자경고종목 risk:투자위험종목
        date (dtm.date, optional): 조회할 날짜. 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame|None: 경보 종목 리스트. 해당일에 저장된 데이터가 없으면 None, 저장되었지만 지정 종목이 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - name (str): 종목명
        - market (str): 거래소
        - designated_date (str): 지정일
        - released_date (str): 해제일

    Examples:
        >>> df = get_invest_alert_stocks('caution', dtm.date(2018, 1, 3))
        >>> print(df.head())
                    name  market designated_date released_date
        code
        038540    상상인  KOSDAQ        20180102      20180103
        073570  리튬포어스  KOSDAQ        20180102      20180103
        123860   아나패스  KOSDAQ        20180102      20180103
        199800     툴젠  KOSDAQ        20180102      20180103
        215100   로보로보  KOSDAQ        20180102      20180103
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/invest-alert-stocks/{alert_type}"
    params = {}
    if date:
        params["date"] = date

    r = send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

        df = pd.DataFrame(r.json())
        if not df.empty:
            for column in ["designated_at", "released_at"]:
                if column in df.columns:
                    df[column] = df[column].apply(_isoformat_to_readable)
                else:
                    df[column] = ""
            df = df[["code", "name", "market", "designated_at", "released_at"]]
            df.rename(columns={"designated_at": "designated_date", "released_at": "released_date"}, inplace=True)
            df.set_index("code", inplace=True)
        return df


def get_management_stocks(date: dtm.date = None) -> Optional[pd.DataFrame]:
    """
    관리종목을 조회합니다.

    2024년 3월 25일 데이터 부터 조회 가능합니다.

    Args:
        date (dtm.date, optional): 조회할 날짜(지정일이 아닌 데이터 수집일). 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame|None: 관리종목 리스트. 해당일에 저장된 데이터가 없으면 None, 저장되었지만 지정 종목이 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - name (str): 종목명
        - current_price (int): 현재가
        - change (int): 전일대비가격
        - change_rate (float): 전일대비등락율
        - volume (int): 거래량
        - designation_date (str): 지정일
        - designation_reason (str): 지정사유

    Examples:
        >>> df = get_management_stocks()
        >>> print(df.head())
                   name  current_price  change  change_rate  volume designation_date designation_reason
        code
        001140       국보           2110       0         0.00       0       2024.03.22          감사의견 의견거절
        006380      카프로            732       0         0.00       0       2024.03.22          감사의견 의견거절
        093230     이아이디           1392       0         0.00       0       2024.03.22          감사의견 의견거절
        363280   티와이홀딩스           3205     150        -4.47  393547       2024.03.22  감사범위제한으로인한 감사의견한정
        36328K  티와이홀딩스우           4940     560       -10.18   26011       2024.03.22  감사범위제한으로인한 감사의견한정
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/management-stocks"
    params = {}
    if date:
        params["date"] = date

    r = send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

        df = pd.DataFrame(r.json())
        if not df.empty:
            df.set_index("code", inplace=True)
        return df


def get_administrative_stocks(date: dtm.date = None) -> Optional[pd.DataFrame]:
    """
    관리종목을 조회합니다.

    2018년 1월 1일 데이터부터 조회 가능합니다.

    Args:
        date (dtm.date, optional): 조회할 날짜(지정일이 아닌 데이터 수집일). 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame|None: 관리종목 리스트. 해당일에 저장된 데이터가 없으면 None, 저장되었지만 지정 종목이 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - name (str): 종목명
        - market (str): 거래소
        - designated_date (str): 지정일
        - released_date (str): 해제일

    Examples:
        >>> df = get_administrative_stocks(dtm.date(2019, 1, 2))
        >>> print(df.head())
                    name market designated_date released_date
        code
        002250  알보젠코리아  KOSPI        20180402
        005090  SGC에너지  KOSPI        20180329      20190319
        010420  한솔피엔에스  KOSPI        20180328      20190225
        140910    에이리츠  KOSPI        20180314      20190312
        011230  삼화전자공업  KOSPI        20180815      20190326
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/administrative-stocks"
    params = {}
    if date:
        params["date"] = date

    r = send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

        df = pd.DataFrame(r.json())
        if not df.empty:
            for column in ["designated_at", "released_at"]:
                if column in df.columns:
                    df[column] = df[column].apply(_isoformat_to_readable)
                else:
                    df[column] = ""
            df = df[["code", "name", "market", "designated_at", "released_at"]]
            df.rename(columns={"designated_at": "designated_date", "released_at": "released_date"}, inplace=True)
            df.set_index("code", inplace=True)
        return df


def _isoformat_to_readable(isodate: str) -> str:
    if isodate and isinstance(isodate, str):
        date = dtm.datetime.fromisoformat(isodate)
        return date.strftime("%Y%m%d")
    return ""


# _get_tickers가 메모이제이션 되어있어서 해당 함수는 캐싱하면 안됨
# 특히 date가 None으로 쓰는경우가 많은데 캐싱하면 오작동함
def get_tickers(
    date: Optional[dtm.date] = None,
    market: Optional[str] = None,
    adjusted: Optional[bool] = True,
    exchange: Union[str, DataExchange] = "KRX",
):
    """
    주어진 날짜와 시장에 따른 주식 종목 코드와 관련 정보를 조회합니다.

    이 함수는 지정된 날짜(기본값은 오늘)와 선택적 시장('KOSPI', 'KOSDAQ')에 대한 주식 종목 코드와 추가 정보를 API를 통해 요청합니다.
    반환된 정보는 pandas DataFrame 형태로 제공되며, 데이터가 없는 경우 빈 DataFrame을 반환합니다. DataFrame은 'code'를 인덱스로 사용합니다.

    KRX 거래소에서는 거래정지 종목 등이 포함되어 있으나, NXT 거래소에서는 거래정지 종목이 제외되어 있습니다.

    KRX 거래소는 2018년 1월 1일 데이터 부터 조회 가능합니다. 수정주가는 소수점 첫째 자리에서 반올림합니다.

    NXT 거래소는 2025년 3월 4일 데이터 부터 조회 가능합니다. 수정주가는 소수점 첫째 자리에서 반올림합니다.

    Args:
        date (Optional[dtm.date]): 조회할 날짜. 기본값은 현재 날짜입니다.
        market (Optional[str]): 조회할 시장. 'KOSPI' 또는 'KOSDAQ' 중 선택할 수 있습니다. 기본값은 None 이며, 모든 시장을 조회합니다.
        adjusted (Optional[bool]): 수정주가 여부. 기본값은 True.
        exchange (Union[str, DataExchange]): 조회할 거래소. 'KRX' 또는 'NXT' 중 선택할 수 있습니다. 기본값은 'KRX' 입니다.

    Returns:
        pd.DataFrame: 주식 종목 코드와 관련 정보를 포함하는 DataFrame. 'code' 컬럼은 인덱스로 설정됩니다.

        - market (str): 시장 이름 (KOSPI 또는 KOSDAQ)
        - name (str): 종목 이름
        - type (str): 종목 유형 (EQUITY, ETF, ETN)
        - reference_price (int): 기준가
        - upper_limit (int or None): 상한가
        - lower_limit (int or None): 하한가
        - previous_close (int): 전일 종가
        - listing_date (str or None): 상장일

    Raises:
        AssertionError: 잘못된 시장이나 거래소 이름이 입력된 경우 오류를 발생시킵니다.
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> tickers = get_tickers()
        >>> print(tickers)
                market     name    type  reference_price  upper_limit  lower_limit  previous_close listing_date delisting_date
        code
        000020   KOSPI     동화약품  EQUITY             7820        10160         5480            7820     19760324
        000040   KOSPI    KR모터스  EQUITY              571          742          400             571     19760525
        000050   KOSPI       경방  EQUITY             6050         7860         4240            6050     19560303
        000070   KOSPI    삼양홀딩스  EQUITY            71100        92400        49800           71100     19681227
        000075   KOSPI   삼양홀딩스우  EQUITY            54200        70400        38000           54200     19920221
    """
    if market:
        assert market in [
            "KOSPI",
            "KOSDAQ",
        ], "market은 'KOSPI' 또는 'KOSDAQ'이어야 합니다."

    assert exchange in [
        "KRX", "NXT", DataExchange.KRX, DataExchange.NXT
    ], "exchange는 'KRX' 또는 'NXT'이어야 합니다."

    exchange = DataExchange.validate(exchange)

    if date is None:
        date = dtm.date.today()
        schedule = get_market_schedule(date)
        if schedule.full_day_closed:
            date = get_last_trading_day(date)

    # 2025년 3월 4일 이전 NXT 거래소 요청 시 빈 데이터 반환
    if exchange == DataExchange.NXT and date < dtm.date(2025, 3, 4):
        return pd.DataFrame()

    return _get_tickers(date, market, adjusted, exchange)


def _get_tickers_check_not_expected_res(res):
    """
    get_tickers 함수에서 캐싱할 값인지 체크하는 함수
    """
    return (res is None) or res.empty


@domesticCache.memoize(not_expected_res=_get_tickers_check_not_expected_res)
def _get_tickers(date: dtm.date, market: str = None, adjusted: bool = True, exchange: DataExchange = DataExchange.KRX):
    """
    get_tickers 함수의 실제 구현부.
    기존 함수에선 date가 None이어도 정상적으로 돌아서 메모이제이션 하기 좋지않았음.
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/tickers/{date.strftime('%Y%m%d')}"
    params = {
        "adjusted": "true" if adjusted else "false",
        "current_date": dtm.date.today(),
        "exchange": exchange.value,
    }
    if market:
        params["market"] = market

    r = send_request("GET", url, params=params)
    raise_for_status(r)

    data = r.json()
    rows = data["rows"]
    cols = data["cols"]

    if len(rows) == 0:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=cols)
    df.set_index("code", inplace=True)

    if adjusted:
        for col in ["reference_price", "upper_limit", "lower_limit", "previous_close"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: quantize_adjusted_price(x) if pd.notna(x) else x)

    # None 값 처리: upper_limit, lower_limit, previous_close
    mask_upper_limit = df["upper_limit"].isna()
    mask_lower_limit = df["lower_limit"].isna()
    mask_previous_close = df["previous_close"].isna()

    # reference_price 기준으로 상한가/하한가 계산
    if "reference_price" in df.columns:
        # 상한가/하한가 계산 함수
        def calculate_price_limit(row):
            price = row["reference_price"]
            market = row["market"]
            etf_etn = row["type"] == "ETF" or row["type"] == "ETN"

            tick_size = get_krx_tick_size(price, etf_etn, market, date)

            # 상한가 계산 (1.3배) 후 호가단위로 절삭 (내림)
            upper = price * 1.3
            upper = int(upper // tick_size * tick_size)

            # 하한가 계산 (0.7배) 후 호가단위로 절삭 (올림)
            lower = price * 0.7
            lower = int((lower + tick_size - 0.01) // tick_size * tick_size)

            return pd.Series([upper, lower])

        # 상한가/하한가 계산 적용
        if mask_upper_limit.any() or mask_lower_limit.any():
            limits = df.loc[mask_upper_limit | mask_lower_limit].apply(calculate_price_limit, axis=1)
            if not limits.empty:
                df.loc[mask_upper_limit, "upper_limit"] = limits[0]
                df.loc[mask_lower_limit, "lower_limit"] = limits[1]

        # previous_close 채우기
        df.loc[mask_previous_close, "previous_close"] = df.loc[mask_previous_close, "reference_price"]

    df = df.astype({"reference_price": int, "upper_limit": int, "lower_limit": int, "previous_close": int})

    return df


# 8시간 캐시하면 언제 돌려도 9시 개장 전엔 당일 데이터를 받을 수 있음
@domesticCache.memoize(expire=8 * 60 * 60, not_expected_res=_get_tickers_check_not_expected_res)
def get_ticker_info(code: str) -> Optional[pd.DataFrame]:
    """
    종목의 기본정보를 조회합니다.

    Args:
        code (str): 조회할 종목의 코드

    Returns:
        pd.DataFrame|None: 기본정보 리스트. 데이터가 없으면 None

        - code (str, index): 종목코드
        - isin (str): 국제 증권 식별 번호
        - name (str): 이름
        - market (str): 거래소
        - type (str): 종목유형. EQUITY(일반상품), ETF, ETN
        - listing_date (str): 상장일

    Examples:
        >>> df = get_ticker_info("032040")
        >>> print(df)
                isin	name	market	type	full_name	listing_date	delisting_date
        code
        032040	KR7032040008	씨앤에스자산관리	KOSDAQ	EQUITY	주식회사 씨앤에스자산관리	19970123	20181011

    """
    return _ticker_request("code", code)


def find_ticker_info(name: str) -> Optional[pd.DataFrame]:
    """
    종목명으로 기본정보를 조회합니다.

    Args:
        name (str): 조회할 종목의 이름

    Returns:
        pd.DataFrame|None: 기본정보 리스트. 데이터가 없으면 None

    Examples:
        >>> df = find_ticker_info("삼성")
        >>> print(df.head())
                isin   name market    type     full_name listing_date delisting_date
        code
        000810  KR7000810002   삼성화재  KOSPI  EQUITY      삼성화재해상보험     19750630
        000815  KR7000811000  삼성화재우  KOSPI  EQUITY  삼성화재해상보험1우선주     19900410
        001360  KR7001360007   삼성제약  KOSPI  EQUITY          삼성제약     19750704
        005930  KR7005930003   삼성전자  KOSPI  EQUITY          삼성전자     19750611
        005935  KR7005931001  삼성전자우  KOSPI  EQUITY      삼성전자1우선주     19890925

    """
    return _ticker_request("name", name)


def _ticker_request(type: str, value: str):
    url = f"{c.PYQQQ_API_URL}/domestic-stock/tickers"
    params = {type: value}

    r = send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

    response = r.json()
    if response is None:
        return None

    ticker_list = [response] if type == "code" else response
    df = pd.DataFrame(ticker_list)

    if not df.empty:
        # 열이 없는 경우 기본값으로 초기화
        for col in ["listing_date", "delisting_date"]:
            if col not in df.columns:
                df[col] = ""

        df = df[["code", "isin", "name", "market", "type", "full_name", "listing_date", "delisting_date"]]
        df.set_index("code", inplace=True)

    return df


def get_rising_stocks(market: str, time: Union[dtm.datetime, dtm.date]) -> pd.DataFrame:
    """
    지정된 시장과 시간에 따른 상승 주식 목록을 조회합니다.

    이 함수는 주어진 시장('KOSPI' 또는 'KOSDAQ')과 날짜 및/또는 시간에 대해 상승하는 주식들의 데이터를 API를 통해 요청합니다.
    휴장일인 경우 빈 DataFrame을 반환합니다. 요청한 날짜 및 시간에 대한 데이터가 없는 경우에도 빈 DataFrame을 반환하며,
    요청이 실패하면 예외를 발생시킵니다. 반환된 데이터는 'code'를 인덱스로 사용하는 DataFrame 형태로 제공됩니다.

    시간은 30분 단위로만 제공됩니다. 예를 들어 9시 30분, 10시 00분, 10시 30분 등으로만 조회할 수 있습니다.
    그 외의 시간은 30분 단위로 내림하여 조회합니다. 예를 들어 9시 15분은 9시 00분으로 조회합니다.

    2024년 5월 3일 데이터 부터 조회 가능합니다.

    Args:
        market (str): 조회할 주식 시장의 명칭. 'KOSPI' 또는 'KOSDAQ' 중 하나여야 합니다.
        time (dtm.datetime | dtm.date): 조회할 날짜와 시간. 시간이 제공되지 않은 경우 시장 종료 시간을 사용합니다.

    Returns:
        pd.DataFrame: 주식 데이터를 포함하는 DataFrame. 'code'를 인덱스로 사용합니다.

    Raises:
        AssertionError: 잘못된 시장 명칭이 입력된 경우.
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> stocks = get_rising_stocks("KOSPI", dtm.datetime.now())
        >>> print(stocks)
                rank     name  current_price  change  change_rate    volume  bid_price  ask_price  bid_volume  ask_volume    per    roe
        code
        090460     1     비에이치          20700    3060        17.35  14705798      20700      20750      107635      194628   7.87  15.11
        004090     2     한국석유          17150    2050        13.58  12984410      17150      17160       21096        4507  14.66   8.67
        002380     3      KCC         280500   33000        13.33    140193     280000     280500        1259        5112  11.72   4.13
        018880     4    한온시스템           6490     620        10.56   4428320       6480       6490       24297      146398  67.60   2.21
        025620     5  제이준코스메틱           7710     710        10.14   1231670       7700       7710         677        6139  -4.96 -16.66
    """

    assert market in ["KOSPI", "KOSDAQ"], "market은 'KOSPI' 또는 'KOSDAQ'이어야 합니다."

    if isinstance(time, dtm.datetime):
        schedule = get_market_schedule(time.date())
        if schedule.full_day_closed:
            return pd.DataFrame()
    elif isinstance(time, dtm.date):
        schedule = get_market_schedule(time)
        if schedule.full_day_closed:
            return pd.DataFrame()

        time = dtm.datetime.combine(time, schedule.close_time)
    else:
        raise ValueError("time은 datetime 또는 date 객체여야 합니다.")

    url = f"{c.PYQQQ_API_URL}/domestic-stock/rising-stocks/{market}/{time.date()}/{time.strftime('%H%M')}"
    r = send_request("GET", url)
    if r.status_code == 404:
        return pd.DataFrame()
    else:
        raise_for_status(r)

    df = pd.DataFrame(r.json())

    if not df.empty:
        df.set_index("code", inplace=True)

    return df


def get_overheat_stocks(date: dtm.date = None) -> Optional[pd.DataFrame]:
    """
    단기과열종목을 조회합니다.

    2018년 1월 1일 데이터 부터 조회 가능합니다. 단기과열종목이 연장되면 연장시점을 기준으로 지정일, 해제일이 표시됩니다.

    Args:
        date (dtm.date, optional): 조회할 날짜(지정일이 아닌 데이터 수집일). 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame|None: 단기과열종목 리스트. 해당일에 저장된 데이터가 없으면 None, 저장되었지만 지정 종목이 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - name (str): 종목명
        - market (str): 거래소
        - designated_date (str): 지정일
        - released_date (str): 해제일

    Examples:
        >>> df = get_overheat_stocks(dtm.date(2024, 10, 17))
        >>> print(df.head())
                        name market designated_date released_date
        code
        001515   SK증권우  KOSPI        20241016      20241021
        001525     동양우  KOSPI        20241016      20241021
        002785  진흥기업우B  KOSPI        20241016      20241021
        004105   태양금속우  KOSPI        20241016      20241021
        004415   서울식품우  KOSPI        20241016      20241021
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/overheat-stocks"
    params = {}
    if date:
        params["date"] = date

    r = send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        raise_for_status(r)

        df = pd.DataFrame(r.json())
        if not df.empty:
            for column in ["designated_at", "released_at"]:
                if column in df.columns:
                    df[column] = df[column].apply(_isoformat_to_readable)
                else:
                    df[column] = ""
            df = df[["code", "name", "market", "designated_at", "released_at"]]
            df.rename(columns={"designated_at": "designated_date", "released_at": "released_date"}, inplace=True)
            df.set_index("code", inplace=True)
        return df


def get_market_cap(date: dtm.date = None) -> pd.DataFrame:
    """
    시가총액 및 발행주식 정보를 조회합니다.

    2018년 1월 1읿 데이터 부터 조회가능합니다. 시가총액은 조회 일자의 종가를 기준으로 계산되어 있습니다.

    Args:
        date (dtm.date, optional): 조회할 날짜. 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame: 종목별 정보. 해당일에 저장된 데이터가 없으면 빈 DataFrame이 반환됩니다.

        - code (str): 종목코드.
        - market (str): 거래소.
        - type (str): 종목 유형 (EQUITY, ETF, ETN).
        - value (int): 시가총액.
        - shares (int): 상장주식수.

    Examples:
        >>> df = get_market_cap(dtm.date(2024, 1, 9))
        >>> print(df)
                    market    type         value    shares
            code
            000020   KOSPI  EQUITY  296352896700  27931470
            000040   KOSPI  EQUITY   34033016610  96138465
            000050   KOSPI  EQUITY  248656498900  27415270
            000070   KOSPI  EQUITY  566954740200   8564271
            000075   KOSPI  EQUITY   15750204400    304058
            ...        ...     ...           ...       ...
            950170  KOSDAQ  EQUITY  194616971010  50288623
            950190  KOSDAQ  EQUITY  157255149360  13579892
            950200  KOSDAQ  EQUITY  109645502100  19236053
            950210   KOSPI  EQUITY  576322126450  60096155
            950220  KOSDAQ  EQUITY  191011942380  98867465
    """

    url = f"{c.PYQQQ_API_URL}/domestic-stock/marketcap/all"
    params = {}
    if date:
        params["date"] = date

    r = send_request("GET", url, params=params)
    raise_for_status(r)

    rows = r.json()
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.astype(
            {
                "value": np.int64,
                "shares_outstanding": np.int64,
            }
        )
        df.rename(columns={"shares_outstanding": "shares"}, inplace=True)
        df = df[["code", "market", "type", "value", "shares"]]
        df.set_index("code", inplace=True)

    return df


def get_market_cap_by_codes(codes: List[str], date: dtm.date = None) -> pd.DataFrame:
    """
    지정한 종목들의 시가총액 및 발행주식 정보를 조회합니다.

    2018년 1월 1읿 데이터 부터 조회가능합니다. 시가총액은 조회 일자의 종가를 기준으로 계산되어 있습니다.

    Args:
        codes (list[str]): 종목 코드 리스트
        date (dtm.date, optional): 조회할 날짜. 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame: 종목별 정보. 해당일에 저장된 데이터가 없으면 빈 DataFrame이 반환됩니다.

        - code (str): 종목코드.
        - market (str): 거래소.
        - type (str): 종목 유형 (EQUITY, ETF, ETN).
        - value (int): 시가총액.
        - shares (int): 상장주식수.

    Examples:
        >>> df = get_market_cap_by_codes(["005930", "319640", "068270"], dtm.date(2024, 11, 4))
        >>> print(df)
            market    type            value      shares
        code
        005930  KOSPI  EQUITY  350426235685000  5969782550
        068270  KOSPI  EQUITY   40669771006000   217021190
        319640  KOSPI     ETF      54381500000     3050000
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/marketcap/codes"
    chunks = chunk(codes, 200)

    output = []
    for i, asset_codes in enumerate(chunks):
        params = {
            "codes": ",".join(asset_codes),
        }
        if date:
            params["date"] = date

        r = send_request("GET", url, params=params)
        raise_for_status(r)

        rows = r.json()
        df = pd.DataFrame(rows)
        output.append(df)

    if not output:
        return pd.DataFrame()

    df = pd.concat(output)
    if not df.empty:
        df = df.astype(
            {
                "value": np.int64,
                "shares_outstanding": np.int64,
            }
        )
        df.rename(columns={"shares_outstanding": "shares"}, inplace=True)
        df = df[["code", "market", "type", "value", "shares"]]
        df.set_index("code", inplace=True)

    return df


def get_investor_net_purchases(date: dtm.date = None):
    """
    투자자별 거래실적을 조회합니다.

    2024년 1월 1일 데이터 부터 조회 가능합니다. 2024년 10월 24일 이전에 상장폐지된 종목은 지원되지 않습니다.

    Args:
        date (dtm.date, optional): 조회할 날짜. 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame: 경보 종목 리스트. 해당일에 저장된 데이터가 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - market (str): 시장 이름 (KOSPI 또는 KOSDAQ)
        - type (str): 종목 유형 (EQUITY, ETF, ETN)
        - institutional (int): 기관 순매수량
        - others (int): 기타법인 순매수량
        - individual (int): 개인 순매수량
        - foreign (int): 외국인 순매수량

    Examples:
        >>> df = get_investor_net_purchases(dtm.date(2024, 1, 2))
        >>> print(df.head())
                    market    type  institutional  others  individual  foreign
        code
        000020  KOSPI  EQUITY           8301    5391      -86001    72309
        000040  KOSPI  EQUITY              3   -6125       45701   -39579
        000050  KOSPI  EQUITY             28       0         -14      -14
        000070  KOSPI  EQUITY          -4978    3200        3778    -2000
        000075  KOSPI  EQUITY             10       0         -10        0
    """

    url = f"{c.PYQQQ_API_URL}/domestic-stock/investor/all"
    params = {}
    if date:
        params["date"] = date

    r = send_request("GET", url, params=params)
    raise_for_status(r)

    rows = r.json()
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[["code", "market", "type", "institutional", "others", "individual", "foreign"]]
        df.set_index("code", inplace=True)

    return df
