from types import NoneType
from pyqqq.utils.api_client import send_request, raise_for_status
from typing import List, Union
import json
import pyqqq.config as c


class KVStore:
    """
    Simple key-value store

    Args:
        context_name (str, optional): 전략 등 DB 구분을 위한 context 식별자. 기본값은 "default".
    """

    def __init__(self, context_name: str = "default"):
        self.name = context_name

    def get(self, key: str) -> Union[str, bool, int, float, dict, list, None]:
        """
        KV store 로 부터 key 에 해당하는 값을 가져온다.

        Args:
            key (str): key

        Returns:
            str | bool | int | float | dict | list | None: value
        """
        assert type(key) is str, "key must be a string"
        assert len(key) > 0, "key must not be empty"

        url = f"{c.PYQQQ_API_URL}/kvstore/get-value"
        params = {"contextName": self.name, "key": key}
        r = send_request("GET", url, params=params)
        raise_for_status(r)

        if len(r.text) == 0:
            return None

        data = r.json()
        if data:
            return json.loads(data)
        else:
            return None

    def set(
        self, key: str, value: Union[str, bool, int, float, dict, list, None]
    ) -> bool:
        """
        KV store 에 key 에 해당하는 값을 저장한다.

        value는 json.dumps로 serialize 가능한 값이어야 한다.
        value가 None이면 key를 삭제한다. (delete 메소드와 동일한 효과)


        Args:
            key (str): key
            value (str | bool | int | float | dict | list | None): value

        Returns:
            bool: 성공 여부
        """
        assert type(key) is str, "key must be a string"
        assert len(key) > 0, "key must not be empty"
        assert type(value) in [
            str,
            bool,
            int,
            float,
            dict,
            list,
            NoneType,
        ], "value must be a string, bool, int, float, dict, list, or None"

        if value is None:
            return self.delete(key)

        try:
            value = json.dumps(value)
        except Exception:
            raise ValueError("value must be serializable to JSON")

        req_body = {
            "contextName": self.name,
            "key": key,
            "value": value,
        }

        r = send_request("PUT", f"{c.PYQQQ_API_URL}/kvstore/set-value", json=req_body)
        raise_for_status(r)

        data = r.json()
        return data.get("message") == "success"

    def delete(self, key: str) -> bool:
        """
        KV store 에서 key 에 해당하는 값을 삭제한다.

        Args:
            key (str): key

        Returns:
            bool: 성공 여부
        """
        req_body = {
            "contextName": self.name,
            "key": key,
        }

        r = send_request("DELETE", f"{c.PYQQQ_API_URL}/kvstore/delete-value", json=req_body)
        raise_for_status(r)

        if r.status_code != 200:
            print(r.text)

        data = r.json()
        return data.get("message") == "success"

    def keys(self) -> List[str]:
        """
        KV store 에 저장된 모든 key 를 가져온다.

        Returns:
            List[str]: key list
        """
        url = f"{c.PYQQQ_API_URL}/kvstore/list-keys"
        r = send_request("GET", url, params={"contextName": self.name})
        raise_for_status(r)

        data = r.json()

        return data if data else []

    def clear(self):
        """
        KV store 에 저장된 모든 key-value 를 삭제한다.
        """
        url = f"{c.PYQQQ_API_URL}/kvstore/clear"
        r = send_request("DELETE", url, json={"contextName": self.name})
        raise_for_status(r)


class MockKVStore(KVStore):
    """
    Mock KVStore for testing
    """

    def __init__(self, context_name: str = "default"):
        super().__init__(context_name)
        self.store = {}

    def get(self, key: str) -> Union[str, bool, int, float, dict, list, None]:
        return self.store.get(key)

    def set(self, key: str, value: Union[str, bool, int, float, dict, list, None]) -> bool:
        if value is None:
            return self.delete(key)

        self.store[key] = value
        return True

    def delete(self, key: str) -> bool:
        if key in self.store:
            del self.store[key]
            return True
        return False

    def keys(self) -> List[str]:
        return list(self.store.keys())

    def clear(self):
        self.store = {}
