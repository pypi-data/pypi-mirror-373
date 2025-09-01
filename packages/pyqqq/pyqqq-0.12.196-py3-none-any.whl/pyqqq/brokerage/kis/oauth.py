from pyqqq import get_api_key
from pyqqq.utils.kvstore import KVStore
from tinydb import TinyDB, Query
from typing import Optional, Tuple
import datetime as dtm
import pyqqq.config as c
import requests


class KISAuth:
    '''
    한국투자증권 인증 정보를 담고 있는 객체

    Args:
        appkey (str): 앱 키
        appsecret (str): 앱 시크릿
        paper_trading (bool): 모의 투자 여부
    '''
    def __init__(self, appkey: str, appsecret: str, paper_trading: bool = False):
        assert appkey is not None, "App key must be set"
        assert appsecret is not None, "App secret must be set"

        self.appkey = appkey
        self.appsecret = appsecret
        self.paper_trading = paper_trading
        self.repo = KISTokenRepository()

    @property
    def host_url(self) -> str:
        '''
        모의/실전 투자 환경에 따른 API 호스트 URL을 반환합니다.

        Returns:
            str: API 호스트 URL
        '''
        if self.paper_trading:
            return 'https://openapivts.koreainvestment.com:29443'
        else:
            return 'https://openapi.koreainvestment.com:9443'

    @property
    def websocket_url(self) -> str:
        """
        모의/실전 투자 환경에 따른 웹소켓 호스트 URL을 반환합니다.

        Returns:
            str: 웹소켓 호스트 URL
        """
        if self.paper_trading:
            return "ws://ops.koreainvestment.com:31000"
        else:
            return "ws://ops.koreainvestment.com:21000"

    def get_token(self, refresh=False) -> str:
        '''
        액세스 토큰을 반환합니다.

        Args:
            refresh (bool): 강제 재발급

        Returns:
            str: 액세스 토큰
        '''
        token = self.repo.find(KISKeyTypes.ACCESS_TOKEN, self.appkey, self.appsecret)
        if token is None or refresh is True:
            token, expiry = self.issue_access_token()
            self.repo.save(
                KISKeyTypes.ACCESS_TOKEN, self.appkey, self.appsecret, token, expiry
            )

        return token

    def issue_access_token(self):
        '''
        액세스 토큰을 발급합니다.

        Returns:
            tuple: 액세스 토큰과 만료 시간을 담은 튜플
        '''
        if self.appkey is None or self.appsecret is None:
            raise ValueError('App key and app secret must be set')

        headers = {
            'content-type': 'application/json'
        }
        body = {
            'grant_type': 'client_credentials',
            'appkey': self.appkey,
            'appsecret': self.appsecret
        }

        r = requests.post(f"{self.host_url}/oauth2/tokenP", headers=headers, json=body)
        r.raise_for_status()

        data = r.json()

        access_token = data['access_token']
        expires_in = data['expires_in']
        expiry = int(dtm.datetime.now().timestamp() + expires_in)

        return access_token, expiry

    def get_approval_key(self, refresh=False) -> str:
        """
        승인 키를 반환합니다.

        Args:
            refresh (bool): 강제 재발급

        Returns:
            str: 승인 키
        """
        approval_key = self.repo.find(
            KISKeyTypes.APPROVAL_KEY, self.appkey, self.appsecret
        )
        if approval_key is None or refresh is True:
            approval_key, expiry = self.issue_approval_key()
            self.repo.save(
                KISKeyTypes.APPROVAL_KEY,
                self.appkey,
                self.appsecret,
                approval_key,
                expiry,
            )

        return approval_key

    def issue_approval_key(self) -> Tuple[str, str]:
        """
        승인 키를 발급합니다.

        Returns:
            tuple: 승인 키와 만료 시간을 담은 튜플
        """
        headers = {"content-type": "application/json; utf-8"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "secretkey": self.appsecret,
        }

        r = requests.post(
            f"{self.host_url}/oauth2/Approval", headers=headers, json=body
        )
        r.raise_for_status()

        data = r.json()
        approval_key = data["approval_key"]
        expiry = int(
            (dtm.datetime.now() + dtm.timedelta(hours=23, minutes=30)).timestamp()
        )
        return approval_key, expiry


class KISTokenRepository:
    def __init__(self):
        if get_api_key():
            self.repo = _RemoteTokenRepository()
        else:
            self.repo = _LocalTokenRepository()

    def find(self, type, appkey, appsecret) -> Optional[str]:
        """
        앱 키와 앱 시크릿에 해당하는 액세스 토큰을 반환합니다.

        Args:
            type (str): 토큰 타입 (access_token, approval_key)
            appkey (str): 앱 키
            appsecret (str): 앱 시크릿

        Returns:
            str|None: 액세스 토큰
        """
        return self.repo.find(type, appkey, appsecret)

    def save(self, type, appkey, appsecret, token, expiry):
        """
        앱 키와 앱 시크릿에 해당하는 액세스 토큰을 저장합니다.

        Args:
            type (str): 토큰 타입 (access_token, approval_key)
            appkey (str): 앱 키
            appsecret (str): 앱 시크릿
            token (str): 액세스 토큰
            expiry (int): 만료 시간(UNIX 타임스탬프)
        """
        return self.repo.save(type, appkey, appsecret, token, expiry)


class KISKeyTypes:
    ACCESS_TOKEN = "access_token"
    APPROVAL_KEY = "approval_key"


class _LocalTokenRepository:
    def __init__(self):
        self.db = TinyDB(c.get_tiny_db_path())

    def find(self, type, appkey, appsecret) -> Optional[str]:
        TokenCache = Query()

        result = self.db.search(
            TokenCache.type == type
            and TokenCache.appkey == appkey
            and TokenCache.appsecret == appsecret
            and TokenCache.expiry > dtm.datetime.now().timestamp()
        )
        if len(result) > 0:
            return result[0]['token']
        else:
            return None

    def save(self, type, appkey, appsecret, token, expiry):
        TokenCache = Query()
        self.db.upsert(
            {
                "type": type,
                "appkey": appkey,
                "appsecret": appsecret,
                "token": token,
                "expiry": expiry,
            },
            TokenCache.appkey == appkey and TokenCache.appsecret == appsecret,
        )


class _RemoteTokenRepository:
    def __init__(self):
        self.kvstore = KVStore("kis_token_cache")
        self.cache = {}

    def _cache_key(self, type, appkey, appsecret):
        return f"{type}_{appkey}_{appsecret}"

    def find(self, type, appkey, appsecret) -> Optional[str]:
        key = self._cache_key(type, appkey, appsecret)

        # 1st. check local data
        local_data = self.cache.get(key, None)
        if local_data:
            if local_data["expiry"] > dtm.datetime.now().timestamp():
                return local_data["token"]
            else:
                self.cache.pop(key)

        # 2nd. check remote data
        if self.kvstore.get(key):
            remote_data = self.kvstore.get(key)
            if remote_data["expiry"] > dtm.datetime.now().timestamp():
                self.cache[key] = remote_data
                return remote_data["token"]
            else:
                self.kvstore.delete(key)

        return None

    def save(self, type, appkey, appsecret, token, expiry):
        key = self._cache_key(type, appkey, appsecret)
        data = {"token": token, "expiry": expiry}
        self.cache[key] = data
        self.kvstore.set(key, data)
