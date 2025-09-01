def singleton(cls):
    """
    Singleton 데코레이터

    이 데코레이터는 클래스를 싱글톤으로 만들어주는 역할을 합니다.

    Args:
        cls (class): 싱글톤으로 만들 클래스.

    Returns:
        function: 싱글톤 클래스 인스턴스를 반환하는 함수.

    Examples:
        >>> @singleton
        ... class SingletonClass:
        ...     def __init__(self, value):
        ...         self.value = value
        ...
        >>> instance1 = SingletonClass(1)
        >>> instance2 = SingletonClass(2)
        >>> instance1 is instance2
        True
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
