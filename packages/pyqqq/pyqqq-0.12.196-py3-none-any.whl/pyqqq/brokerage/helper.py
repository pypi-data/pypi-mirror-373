import json
import os

import pyqqq.config as c
from pyqqq.brokerage.ebest.domestic_stock import EBestDomesticStock
from pyqqq.brokerage.ebest.oauth import EBestAuth
from pyqqq.brokerage.ebest.simple import EBestSimpleDomesticStock
from pyqqq.brokerage.kis.domestic_stock import KISDomesticStock
from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.brokerage.kis.simple import KISSimpleDomesticStock
from pyqqq.utils.api_client import send_request
from pyqqq.utils.logger import get_bare_logger as get_logger


logger = get_logger(__name__)


class NoConnection:
    """.env 파일 등 계정 정보가 없을 경우"""

    def __init__(self):
        pass


class KISConnection:
    """
    환경변수 파일(.env)에 한투 계정 정보가 있을 경우 브로커 연결을 생성하는 클래스입니다.

    Attributes:
        auth (KISAuth): 인증 객체
        broker_code (str): 브로커 코드
        broker (KISDomesticStock): 일반 거래용 브로커 객체
        broker_simple (KISSimpleDomesticStock): 간편 거래용 브로커 객체
        paper_auth (Optional[KISAuth]): 모의투자 인증 객체
        paper_broker_simple (Optional[KISSimpleDomesticStock]): 모의투자 간편 브로커 객체

    """

    logger = get_logger(__name__ + ".KISConnection")

    def __init__(self):
        app_key = os.getenv("KIS_APP_KEY")
        app_secret = os.getenv("KIS_APP_SECRET")
        account_no = os.getenv("KIS_CANO")
        account_product_code = os.getenv("KIS_ACNT_PRDT_CD")
        hts_id = os.getenv("KIS_HTS_ID")

        self.auth = KISAuth(app_key, app_secret)
        self.broker_code = "kis"
        self.broker = KISDomesticStock(self.auth)
        self.broker_simple = KISSimpleDomesticStock(self.auth, account_no, account_product_code, hts_id)
        self.paper_auth = None
        self.paper_broker_simple = None

        self.logger.info("Connected to KIS")
        if all(k in os.environ for k in ["PAPER_KIS_APP_KEY", "PAPER_KIS_APP_SECRET", "PAPER_KIS_CANO", "PAPER_KIS_ACNT_PRDT_CD"]):
            self.logger.info("Using paper broker")

            paper_app_key = os.getenv("PAPER_KIS_APP_KEY")
            paper_app_secret = os.getenv("PAPER_KIS_APP_SECRET")
            paper_account_no = os.getenv("PAPER_KIS_CANO")
            paper_account_product_code = os.getenv("PAPER_KIS_ACNT_PRDT_CD")

            self.paper_auth = KISAuth(paper_app_key, paper_app_secret, paper_trading=True)
            self.paper_broker_simple = KISSimpleDomesticStock(self.paper_auth, paper_account_no, paper_account_product_code)


class EBestConnection:
    """
    환경변수 파일(.env)에 LS(구 이베스트투자)증권 계정 정보가 있을 경우 브로커 연결을 생성하는 클래스입니다.

    Attributes:
        auth (EBestAuth): 인증 객체
        broker_code (str): 브로커 코드
        broker (EBestDomesticStock): 일반 거래용 브로커 객체
        broker_simple (EBestSimpleDomesticStock): 간편 거래용 브로커 객체
        account_no (str): 계좌 번호
        paper_auth (Optional[EBestAuth]): 모의투자 인증 객체
        paper_broker_simple (Optional[EBestSimpleDomesticStock]): 모의투자 간편 브로커 객체
    """

    logger = get_logger(__name__ + ".EBestConnection")

    def __init__(self):
        self.auth = EBestAuth(os.getenv("EBEST_APP_KEY"), os.getenv("EBEST_APP_SECRET"))
        self.broker_code = "ebest"
        self.broker = EBestDomesticStock(self.auth)
        self.broker_simple = EBestSimpleDomesticStock(self.auth)
        self.account_no = self.broker_simple.get_account().get("account_no")
        self.paper_auth = None
        self.paper_broker_simple = None

        self.logger.info("Connected to EBEST")
        if os.getenv("PAPER_TRADING") == "1":
            self.logger.info("Using paper broker")

            self.paper_auth = EBestAuth(os.getenv("EBEST_APP_KEY"), os.getenv("EBEST_APP_SECRET"), paper_trading=os.getenv("PAPER_TRADING") == "1")
            self.paper_broker_simple = EBestSimpleDomesticStock(self.paper_auth)


def get_base_class():
    if os.getenv("KIS_APP_KEY"):
        return KISConnection
    elif os.getenv("EBEST_APP_KEY"):
        return EBestConnection
    elif os.getenv("ACCOUNT_NICK"):
        return __set_account_info_env(os.getenv("ACCOUNT_NICK"))
    else:
        return NoConnection


def __lookup_account_info(nick: str):
    url = f"{c.PYQQQ_API_URL}/users/me/accounts/{nick}/access"
    r = send_request(
        "POST",
        url,
    )
    if r.status_code > 204:
        logger.error(f"Failed to get day data: {r.text}")
        r.raise_for_status()

    return json.loads(r.json())


def __set_account_info_env(nick: str):
    account = __lookup_account_info(nick)
    if account.get("KIS_APP_KEY"):
        os.environ["KIS_APP_KEY"] = account.get("KIS_APP_KEY") or os.getenv("KIS_APP_KEY")
        os.environ["KIS_APP_SECRET"] = account.get("KIS_APP_SECRET") or os.getenv("KIS_APP_SECRET")
        os.environ["KIS_CANO"] = account.get("KIS_CANO") or os.getenv("KIS_CANO")
        os.environ["KIS_ACNT_PRDT_CD"] = account.get("KIS_ACNT_PRDT_CD") or os.getenv("KIS_ACNT_PRDT_CD")
        os.environ["KIS_HTS_ID"] = account.get("KIS_HTS_ID") or os.getenv("KIS_HTS_ID")
        return KISConnection
    elif account.get("EBEST_APP_KEY"):
        os.environ["EBEST_APP_KEY"] = account.get("EBEST_APP_KEY") or os.getenv("EBEST_APP_KEY")
        os.environ["EBEST_APP_SECRET"] = account.get("EBEST_APP_SECRET") or os.getenv("EBEST_APP_SECRET")
        return EBestConnection
    else:
        return NoConnection


class PyQQQAutoConnectionSingleton(get_base_class()):
    """
    환경변수를 읽어서 자동으로 브로커 연결을 생성하는 싱글톤 클래스입니다.

    이 클래스는 환경변수에 따라 다음과 같은 클래스 중 하나의 인스턴스를 반환합니다:
    - NoConnection: 계정 정보가 없는 경우
    - KISConnection: 한투 계정 정보가 있는 경우
    - EBestConnection: LS(구 이베스트투자)증권 계정 정보가 있는 경우

    Example:
        >>> conn = PyQQQAutoConnectionSingleton()
        >>> conn.broker_simple.get_account()

    Returns:
        NoConnection | KISConnection | EBestConnection: 환경변수에 따라 결정된 브로커 연결 인스턴스
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__()
