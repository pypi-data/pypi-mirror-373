import os
import pyqqq.config as c
import importlib.metadata

__version__ = importlib.metadata.version("pyqqq")

_api_key = None


def set_api_key(api_key: str):
    """
    전역 PyQQQ API 키를 설정합니다.

    이 함수는 주어진 API 키를 전역 변수로 저장합니다. 입력된 API 키는 None이 아니어야 하며, 최소 32자 이상이어야 합니다.

    Args:
        api_key (str): 설정할 API 키.

    Raises:
        AssertionError: API 키가 None이거나 32자 미만일 경우 오류를 발생시킵니다.

    Examples:
        >>> set_api_key("1234567890abcdef1234567890abcdef")
    """

    global _api_key

    assert api_key is not None, "API key must not be None"
    assert len(api_key) >= 32, "API key must be at least 32 characters long"

    _api_key = api_key


def get_api_key() -> str | None:
    """
    설정된 전역 PyQQQ API 키를 반환합니다.

    API 키가 메모리에 저장되어 있으면 그 값을 반환합니다. 저장되어 있지 않다면, 환경 변수나 자격 증명 파일에서
    API 키를 조회하여 반환합니다. 모든 방법이 실패하면 None을 반환합니다.

    Returns:
        str | None: 저장된 API 키 또는 None.

    Examples:
        >>> api_key = get_api_key()
        >>> print(api_key)
    """
    if _api_key:
        return _api_key

    elif c.get_pyqqq_api_key() is not None:
        return c.get_pyqqq_api_key()

    elif os.path.exists(c.get_credential_file_path()):
        with open(c.get_credential_file_path(), "r") as f:
            return f.read().strip()

    return None
