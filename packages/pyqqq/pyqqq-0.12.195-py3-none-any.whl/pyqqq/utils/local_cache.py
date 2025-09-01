import cachetools
import os
import functools
import hashlib

from diskcache import Cache

DEFAULT_CACHE_DIR = ".cache/"
DEFAULT_CACHE_EXPIRE = 60 * 60 * 24 * 7


class DiskCacheManager:

    def __init__(self, cache_name):
        parent_dir = os.getenv("CACHE_DIR") or DEFAULT_CACHE_DIR
        dir_str = os.path.join(parent_dir, cache_name)
        self.use_cache = os.getenv("USE_DISK_CACHE") is not None
        if self.use_cache:
            self.cache = Cache(dir_str)

    def memoize(self, expire=DEFAULT_CACHE_EXPIRE, not_expected_res=None):
        def decorator(func):
            def should_cache(res):
                if callable(not_expected_res):
                    return not not_expected_res(res)
                else:
                    return res is not not_expected_res

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.use_cache:
                    return func(*args, **kwargs)

                cache_key = self._make_cache_key(func, *args, **kwargs)

                if cache_key in self.cache and should_cache(self.cache[cache_key]):
                    return self.cache[cache_key]
                else:
                    res = func(*args, **kwargs)
                    if should_cache(res):
                        self.cache.set(key=cache_key, value=res, expire=expire)
                    return res
            return wrapper
        return decorator

    def _make_cache_key(self, func, *args, **kwargs):
        """
        캐시 키 생성 함수

        :param func: 함수 객체
        :param args: 함수 인자
        :param kwargs: 함수 키워드 인자
        :return: 생성된 캐시 키 (문자열)
        """
        key_base = f"{func.__name__}:{args}:{kwargs}"
        return hashlib.md5(key_base.encode()).hexdigest()


def ttl_cache(maxsize=100, ttl=60):
    """
    TTL 캐시를 제공하는 데코레이터.

    :param maxsize: 캐시의 최대 크기.
    :param ttl: 캐시된 항목의 TTL(초 단위).
    """

    def decorator(func):
        cache = cachetools.TTLCache(maxsize=maxsize, ttl=ttl)

        @functools.wraps(func)
        @cachetools.cached(cache)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return decorator
