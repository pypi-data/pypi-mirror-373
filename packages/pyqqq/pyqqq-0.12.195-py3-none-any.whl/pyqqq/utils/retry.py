import time
from functools import wraps


def retry(exceptions, total_tries=5, delay=0.5, backoff=2, silently: bool = False):
    """
    지정된 예외가 발생할 때 함수 실행을 지정된 횟수만큼 재시도하는 데코레이터입니다.

    이 데코레이터는 함수를 실행 중 예외가 발생했을 때, 주어진 조건에 따라 자동으로 함수를 재시도합니다.
    재시도 간격은 지연시간과 백오프 인자에 의해 결정되며, 모든 시도가 실패하면 최종적으로 예외를 발생시킵니다.

    Args:
        exceptions (Exception or tuple): 재시도를 트리거하는 예외 또는 예외 튜플.
        total_tries (int): 시도할 총 횟수.
        delay (float): 재시도 간 초기 지연 시간(초).
        backoff (float): 백오프 인자; 예를 들어, 2는 각 재시도 간 지연 시간을 두 배로 늘립니다.
        silently (bool): True일 경우 예외 메시지를 출력하지 않습니다.

    Returns:
        function: 예외 발생 시 재시도를 수행하는 함수.

    Examples:
        >>> @retry(Exception, total_tries=3, delay=1, backoff=1, silently=False)
        ... def test_func():
        ...     print("Trying...")
        ...     raise Exception("An error occurred")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_try = 0
            while current_try < total_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    current_try += 1
                    sleep_time = delay * (backoff ** (current_try - 1))
                    if current_try != total_tries:
                        if not silently:
                            print(f"{str(e)}\nRetrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
                    else:
                        print("Max retry attempts reached, aborting.")
                        raise
        return wrapper
    return decorator
