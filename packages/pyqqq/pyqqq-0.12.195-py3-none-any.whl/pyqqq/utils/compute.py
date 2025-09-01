import datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal
from typing import Union


def quantize_krx_price(price: Union[Decimal, int, float], etf_etn: bool, rounding: str = "floor") -> int:
    """
    주어진 가격을 한국거래소(KRX)의 틱 사이즈에 따라 지정된 반올림 방식으로 조정합니다.

    이 함수는 ETF 또는 ETN 여부에 따라 적절한 틱 사이즈를 계산하고, 주어진 가격을 이 틱 사이즈에 맞추어 반올림합니다.
    사용자는 'round', 'ceil', 'floor' 중에서 반올림 방식을 선택할 수 있습니다.

    Args:
        price (Decimal): 반올림할 가격.
        etf_etn (bool): 가격이 ETF 또는 ETN 상품인 경우 True, 그 외는 False.
        rounding (str, optional): 반올림 방식('round', 'ceil', 'floor'). 기본값은 'floor'.

    Returns:
        int: 반올림된 가격.

    Raises:
        ValueError: rounding이 지정된 세 가지 옵션 중 하나가 아닐 경우 오류를 발생시킵니다.

    Examples:
        >>> quantize_krx_price(Decimal('1520.75'), False, 'round')
        1521
        >>> quantize_krx_price(Decimal('1520.75'), True, 'ceil')
        1521
        >>> quantize_krx_price(Decimal('1520.75'), False, 'floor')
        1520
    """

    if rounding not in ["round", "ceil", "floor"]:
        raise ValueError("rounding should be one of ['round', 'ceil', 'floor']")

    price = Decimal(price)

    constant_rounding = {
        "round": ROUND_HALF_UP,
        "ceil": ROUND_CEILING,
        "floor": ROUND_FLOOR,
    }[rounding]

    tick_size = get_krx_tick_size(price, etf_etn)

    return int((price / tick_size).quantize(Decimal("1"), rounding=constant_rounding) * tick_size)


def get_krx_tick_size(
    price: float,
    etf_etn: bool,
    market: str = "KOSPI",
    date: datetime.date = None,
) -> int:
    """
    주어진 가격과 금융 상품 유형에 따라 적절한 호가가격단위를 반환합니다.

    한국거래소(KRX)의 호가가격단위 규칙에 따라, 특정 가격대의 주식 또는 ETF/ETN의 최소 가격 변동 단위(호가가격단위)를 결정합니다.
    입력된 price가 각 가격대의 최소값 미만일 경우 해당하는 호가가격단위를 반환하며, 모든 조건에 부합하지 않는 경우 최대 가격을 반환합니다.

    날짜별 규칙 변경사항:
    - ETF/ETN: 2023-12-11 이전 5원, 이후 2000원 미만 1원/이상 5원
    - 일반 주식: 2023-01-25 이전 market별 규칙, 이후 현재 통합 규칙

    Args:
        price (float): 상품의 가격.
        etf_etn (bool): 상품이 ETF 또는 ETN인 경우 True, 아니면 False.
        market (str): 상품의 시장. 기본값은 "KOSPI".
        date (datetime.date): 상품의 날짜. 기본값은 None.

    Returns:
        int: 결정된 호가가격단위.

    Raises:
        AssertionError: price가 0 이하일 경우 오류를 발생시킵니다.

    Examples:
        >>> get_krx_tick_size(1500, False)
        1
        >>> get_krx_tick_size(2500, False)
        5
        >>> get_krx_tick_size(2500, True)
        1
    """

    assert price > 0, "price should be greater than 0"

    # 날짜가 None인 경우 현재 날짜를 사용
    if date is None:
        date = datetime.date.today()

    conds = []
    max_value = 0

    if etf_etn:
        # 2023년 12월 11일 이전에는 ETF/ETN 상품에 대해 가격에 상관없이 5원
        etf_rule_change_date = datetime.date(2023, 12, 11)
        if date < etf_rule_change_date:
            conds = []  # 조건 없이 max_value로 처리
            max_value = 5
        else:
            conds = [(2000, 1)]
            max_value = 5
    else:
        # 일반 주식: 2023년 1월 25일 이전에는 market에 따른 규칙 적용
        stock_rule_change_date = datetime.date(2023, 1, 25)

        if date < stock_rule_change_date:
            # 2023년 1월 25일 이전: market에 따른 규칙
            if market == "KOSPI":
                conds = [
                    (1000, 1),
                    (5000, 5),
                    (10000, 10),
                    (50000, 50),
                    (100000, 100),
                    (500000, 500),
                ]
                max_value = 1000
            elif market == "KOSDAQ":
                conds = [
                    (1000, 1),
                    (5000, 5),
                    (10000, 10),
                    (50000, 50),
                ]
                max_value = 100
            else:
                # 기본값 (KOSPI 규칙)
                conds = [
                    (1000, 1),
                    (5000, 5),
                    (10000, 10),
                    (50000, 50),
                    (100000, 100),
                    (500000, 500),
                ]
                max_value = 1000
        else:
            # 2023년 1월 25일 이후: 현재 규칙
            conds = [
                (2000, 1),
                (5000, 5),
                (20000, 10),
                (50000, 50),
                (200000, 100),
                (500000, 500),
            ]
            max_value = 1000

    for min_price, size in conds:
        if price < min_price:
            return size

    return max_value


def quantize_adjusted_price(price: float | int) -> int:
    """
    한국거래소 기준 수정주가는 소수점 첫째 자리에서 반올림합니다.

    Args:
        price (float | int): 가격.

    Returns:
        int: 반올림된 가격.
    """
    return int(Decimal(price).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
