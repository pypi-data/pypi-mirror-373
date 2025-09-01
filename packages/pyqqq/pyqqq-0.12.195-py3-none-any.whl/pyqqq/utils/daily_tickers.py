import datetime as dtm
from typing import Optional, Tuple
from functools import lru_cache

import pandas as pd
from pyqqq.data import domestic
from pyqqq.utils.market_schedule import is_full_day_closed, get_last_trading_day
from pyqqq.utils.logger import get_bare_logger as get_logger


class DailyTickers:
    _instance = None
    _initialized = False
    logger = get_logger(__name__ + '.DailyTickers')

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._today = dtm.date.today()
        if is_full_day_closed(self._today):
            self._date = get_last_trading_day(self._today)
        else:
            self._date = self._today
        self._is_before_today_krx_open = True
        self._tickers = None
        self._change_date()

    def _chk_days_passed(self):
        return self._today != dtm.date.today()

    @lru_cache(maxsize=30)  # memory_profiler 로 확인 결과 하루치 fetch 결과가 약 2.5MiB
    @staticmethod
    def fetch_tickers(date: dtm.date, exchange: str) -> pd.DataFrame:
        DailyTickers.logger.debug(f'\tfetch_tickers date={date} cache_info={DailyTickers.fetch_tickers.cache_info()}')
        return domestic.get_tickers(date, exchange=exchange)

    def _change_date(self, date: Optional[dtm.date] = None, force: bool = False):
        """_tickers 가 비었거나 날짜가 바뀌었으면 새로 채워넣는다. 8시 50분 이전에는 NXT 거래소 데이터를 사용한다."""
        if not date:
            if self._chk_days_passed():
                self._today = dtm.date.today()
                if is_full_day_closed(self._today):
                    date = get_last_trading_day(self._today)
                else:
                    date = self._today
            else:
                date = self._date

        if self._today == date:
            if dtm.datetime.now().time() < dtm.time(8, 50) and not self._is_before_today_krx_open:
                self._is_before_today_krx_open = True
                self._tickers = None
            elif dtm.datetime.now().time() >= dtm.time(8, 50) and self._is_before_today_krx_open:
                self._is_before_today_krx_open = False
                self._tickers = None
            else:
                pass
        else:
            self._is_before_today_krx_open = False

        if force:
            DailyTickers.fetch_tickers.cache_clear()
            self._tickers = None

        if self._tickers is None or self._date != date:
            self._date = date
            exchange = "NXT" if self._is_before_today_krx_open else "KRX"
            self.logger.debug(f'\tdate changed. date={self._date} wait for get_tickers()')
            self._tickers = DailyTickers.fetch_tickers(self._date, exchange=exchange)

    def get_tickers(self, date: Optional[dtm.date] = None, force: bool = False) -> pd.DataFrame:
        """
        종목정보 가져오기
        """
        self._change_date(date, force)
        return self._tickers

    def get_ticker_info(self, code: str, date: Optional[dtm.date] = None, force: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """
        종목정보 가져오기
        """
        self._change_date(date, force)

        # self.logger.debug(f'\tget_ticker_info code={code} date={self._date}')
        try:
            name = self._tickers.loc[code, 'name']
            type = self._tickers.loc[code, 'type']
        except KeyError:
            try:
                self._change_date(date, True)
                name = self._tickers.loc[code, 'name']
                type = self._tickers.loc[code, 'type']
            except KeyError:
                self.logger.warning(f'KeyError on get_ticker_info. code={code}')
            return (None, None)

        return (name, type)

    def get_listing_date(self, code: str, date: Optional[dtm.date] = None, force: bool = False) -> Optional[dtm.date]:
        """
        상장일 가져오기
        """
        self._change_date(date, force)

        try:
            list_date = self._tickers.loc[code, 'listing_date']
        except KeyError:
            try:
                self._change_date(date, True)
                list_date = self._tickers.loc[code, 'listing_date']
            except KeyError:
                self.logger.warning(f'KeyError on get_listing_date. code={code}')
            return None

        return dtm.datetime.strptime(list_date, "%Y%m%d").date() if list_date else None

    def get_ticker_upper_limit(self, code: str, date: Optional[dtm.date] = None, force: bool = False) -> Optional[int]:
        """
        상한가 가져오기
        """
        self._change_date(date, force)

        # self.logger.debug(f'\tget_ticker_upper_limit code={code} date={self._date}')
        try:
            upper_limit = self._tickers.loc[code, 'upper_limit']
        except KeyError:
            try:
                self._change_date(date, True)
                upper_limit = self._tickers.loc[code, 'upper_limit']
            except KeyError:
                self.logger.warning(f'KeyError on get_ticker_upper_limit. code={code}')
                return None

        return int(upper_limit) if upper_limit else None
