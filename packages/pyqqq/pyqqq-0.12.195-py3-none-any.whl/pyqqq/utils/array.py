from typing import List


def chunk(arr: List, size: int = 1) -> List[List]:
    """
    주어진 배열을 특정 크기의 하위 배열로 나눕니다.

    이 함수는 주어진 배열 arr을 size 매개변수로 지정된 크기의 여러 하위 배열로 나누어 새로운 리스트로 반환합니다.
    만약 arr의 길이가 size로 나누어떨어지지 않는 경우, 마지막 하위 배열은 나머지 요소들로 구성됩니다.

    Args:
        arr (List): 하위 배열로 나눌 대상이 되는 배열.
        size (int, optional): 하위 배열의 크기. 기본값은 1입니다.

    Returns:
        List[List]: 주어진 size에 따라 나누어진 하위 배열들의 리스트.

    Examples:
        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]

        >>> chunk([1, 2, 3, 4, 5], 3)
        [[1, 2, 3], [4, 5]]
    """
    return [arr[i : i + size] for i in range(0, len(arr), size)]


def find(predicate, iterable):
    """
    주어진 조건을 만족하는 첫 번째 항목을 반환합니다.

    이 함수는 iterable에서 주어진 조건(predicate)을 만족하는 첫 번째 항목을 찾아 반환합니다.
    만약 조건을 만족하는 항목이 없으면 None을 반환합니다.

    Args:
        predicate (callable): 각 항목에 대해 평가할 함수.
        iterable (iterable): 검색할 항목들을 포함하는 iterable 객체.

    Returns:
        object: 조건을 만족하는 첫 번째 항목. 조건을 만족하는 항목이 없으면 None.

    Examples:
        >>> find(lambda x: x > 10, [1, 9, 15, 20])
        15
        >>> find(lambda x: x > 10, [1, 2, 3])
        None
    """
    return next((x for x in iterable if predicate(x)), None)
