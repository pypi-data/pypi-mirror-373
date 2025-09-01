import datetime as dtm
import requests


class EBestAuth:
    """
    LS(구 이베스트투자)증권 인증 정보를 담고 있는 객체

    Args:
        appkey (str): 앱 키
        appsecret (str): 앱 시크릿
        paper_trading (bool): 모의 투자 여부
    """

    def __init__(self, appkey: str, appsecret: str, paper_trading: bool = False):
        self.appkey = appkey
        self.appsecret = appsecret
        self.paper_trading = paper_trading

        self.access_token = None
        self.expired_at: dtm.datetime = None

    @property
    def host_url(self) -> str:
        """
        모의/실전 투자 환경에 따른 API 호스트 URL을 반환합니다.

        Returns:
            str: API 호스트 URL
        """
        return "https://openapi.ls-sec.co.kr:8080"

    @property
    def websocket_url(self) -> str:
        """
        실시간 데이터 스트리밍을 위한 웹소켓 URL을 반환합니다.

        Returns:
            str: 웹소켓 URL
        """
        if self.paper_trading:
            return "wss://openapi.ls-sec.co.kr:29443"
        else:
            return "wss://openapi.ls-sec.co.kr:9443"

    def get_token(self, refresh=False) -> str:
        """
        액세스 토큰을 반환합니다.

        Args:
            refresh (bool): 강제 재발급

        Returns:
            str: 액세스 토큰
        """
        if refresh or (self.access_token is None or self.expired_at < dtm.datetime.now()):
            token, expired_at = self.issue_access_token()

            self.access_token = token
            self.expired_at = expired_at

        return self.access_token

    def issue_access_token(self):
        """
        액세스 토큰을 발급합니다.

        Returns:
            tuple: 액세스 토큰과 만료 시간을 담은 튜플
        """
        if self.appkey is None or self.appsecret is None:
            raise ValueError("App key and app secret must be set")

        headers = {"content-type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "appsecretkey": self.appsecret,
            "scope": "oob",
        }

        r = requests.post(f"{self.host_url}/oauth2/token", headers=headers, data=body)
        r.raise_for_status()

        data = r.json()

        access_token = data["access_token"]
        expires_in = data["expires_in"]

        next_day_am7 = dtm.datetime.now().replace(hour=7, minute=0, second=0, microsecond=0) + dtm.timedelta(days=1)
        expired_at = min(dtm.datetime.now() + dtm.timedelta(seconds=expires_in), next_day_am7)

        return access_token, expired_at
