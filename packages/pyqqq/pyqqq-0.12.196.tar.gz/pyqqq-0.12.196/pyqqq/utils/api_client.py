from pyqqq.utils.retry import retry
import pyqqq
import requests


@retry((requests.HTTPError, requests.ConnectionError, requests.Timeout))
def send_request(method: str, url: str, **kwargs):
    api_key = pyqqq.get_api_key()
    if not api_key:
        raise ValueError("API key is not set")

    return requests.request(
        method=method,
        url=url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
        **kwargs,
    )


def raise_for_status(r: requests.Response):
    if r.status_code != 200:
        print(r.text)

    r.raise_for_status()
