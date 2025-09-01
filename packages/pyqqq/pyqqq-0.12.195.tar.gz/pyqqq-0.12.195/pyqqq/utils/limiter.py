import time


_MAX_CALLS = 5
_PERIOD = 1
_SCOPE = "default"


class CallLimiter:
    """
    API 호출 제한을 관리하기 위한 싱글턴 클래스입니다.

    이 클래스는 API 호출 빈도를 제한하여 너무 많은 요청으로 인해 서비스 제한을 받는 것을 방지합니다.
    이 클래스의 인스턴스는 전역에서 단 하나만 존재하며, 다양한 'scope'에 대한 호출 제한 윈도우를 관리합니다.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CallLimiter, cls).__new__(cls)
            cls._instance.windows = {"default": []}

        return cls._instance

    def wait_limit_rate(self, max_calls: int = _MAX_CALLS, period: float = _PERIOD, scope: str = _SCOPE):
        """
        지정된 시간 간격 동안 최대 호출 횟수를 초과하지 않도록 기다립니다.

        호출 윈도우를 관리하여 max_calls 및 period를 기반으로 호출이 허용될 때까지 대기합니다.
        'scope'에 따라 다른 API 또는 함수 호출에 대해 다른 제한을 설정할 수 있습니다.

        Args:
            max_calls (int): 지정된 시간 동안 허용되는 최대 호출 횟수.
            period (float): 호출 제한을 적용할 시간 간격(초).
            scope (str): 호출 제한을 적용할 범위 또는 이름.

        Examples:
            >>> call_limiter = CallLimiter()
            >>> call_limiter.wait_limit_rate(10, 60, 'api_calls')
        """
        if scope not in self.windows:
            self.windows[scope] = []

        now = time.time()
        window = list(filter(lambda x: now - x < period, self.windows[scope]))
        window_size = len(window)

        if window_size >= max_calls:
            time.sleep(period)
        elif window_size > 0:
            time.sleep(period / max_calls)

        window.append(time.time())
        self.windows[scope] = window


def limit_calls(max_calls: int = _MAX_CALLS, period: float = _PERIOD, scope: str = _SCOPE):
    """
    여러 함수에 대한 호출을 제한하는 데코레이터입니다.

    Args:
        max_calls (int): 최대 호출 횟수
        period (float): 기간(초) 동안의 호출 횟수를 제한합니다.
        scope (str): 호출 제한을 적용할 스코프 이름입니다.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            CallLimiter().wait_limit_rate(max_calls=max_calls, period=period, scope=scope)
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator
