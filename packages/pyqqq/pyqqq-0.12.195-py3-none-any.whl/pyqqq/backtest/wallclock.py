import asyncio
import datetime as dtm
from typing import Optional


class WallClock:
    """실시간 및 백테스팅 모드를 지원하는 시간 관리 클래스입니다.

    이 클래스는 트레이딩 시스템에서 시간을 관리하는 핵심 컴포넌트로,
    실시간 거래와 백테스팅에서 동일한 인터페이스를 제공합니다.
    시간대(timezone) 관리와 시간 변경 이벤트 처리를 지원합니다.

    Example:

    .. highlight:: python
    .. code-block:: python

        # 실시간 모드
        clock = WallClock(live_mode=True)
        current = clock.now()
        await clock.sleep(1)  # 실제 1초 대기

        # 백테스팅 모드
        clock = WallClock(
            live_mode=False,
            start_time=datetime(2023, 1, 1),
            end_time=datetime(2023, 12, 31)
        )
        while clock.is_alive():
            current = clock.now()
            await clock.sleep(60)  # 가상으로 1분 진행

    """

    live_mode: bool
    """ 실시간/백테스팅 모드 구분 """
    tzinfo: Optional[dtm.tzinfo]
    """ 시간대 정보 """
    current_time: Optional[dtm.datetime]
    """ 현재 시간 (백테스팅 모드에서만 사용) """
    end_time: Optional[dtm.datetime]
    """ 종료 시간 (백테스팅 모드에서만 사용) """
    on_time_change: Optional[callable]
    """ 시간 변경 후 호출될 콜백 함수 """
    on_before_time_change: Optional[callable]
    """ 시간 변경 전 호출될 콜백 함수 """

    def __init__(self, live_mode: bool = True, start_time: Optional[dtm.datetime] = None, end_time: Optional[dtm.datetime] = None, tzinfo: Optional[dtm.tzinfo] = None):
        """WallClock 클래스를 초기화합니다.

        Args:
            live_mode (bool, optional): 실시간/백테스팅 모드 구분.
                Defaults to True.
            start_time (Optional[datetime], optional): 백테스팅 시작 시간.
                Defaults to None. live_mode=False일 때만 사용.
            end_time (Optional[datetime], optional): 백테스팅 종료 시간.
                Defaults to None. live_mode=False일 때만 사용.
            tzinfo (Optional[datetime.tzinfo], optional): 시간대 정보.
                Defaults to None.
        """
        self.live_mode = live_mode
        self.tzinfo = tzinfo

        if not live_mode:
            self.current_time = start_time
            self.end_time = end_time if end_time is not None else dtm.datetime.now()

            if self.tzinfo is not None:
                self.current_time = self.current_time.astimezone(self.tzinfo)
                self.end_time = self.end_time.astimezone(self.tzinfo)

        self.on_time_change = None
        self.on_before_time_change = None

    def now(self) -> dtm.datetime:
        """현재 시간을 반환합니다.

        Returns:
            datetime: 현재 시간
                - 실시간 모드: 실제 현재 시간
                - 백테스팅 모드: 시뮬레이션 현재 시간

        Raises:
            ValueError: 백테스팅 모드에서 현재 시간이 실제 시간보다 미래인 경우
        """
        if self.live_mode:
            return dtm.datetime.now(self.tzinfo)
        else:
            if self.current_time > dtm.datetime.now(self.tzinfo):
                raise ValueError("backtesting time is must be less than current time")

            return self.current_time

    def today(self) -> dtm.date:
        """현재 날짜를 반환합니다.

        Returns:
            date: 현재 날짜
        """
        return self.now().date()

    def is_alive(self) -> bool:
        """시계가 동작 중인지 확인합니다.

        Returns:
            bool: 시계 동작 여부
                - 실시간 모드: 항상 True
                - 백테스팅 모드: 현재 시간이 종료 시간 이전이면 True
        """
        if self.live_mode:
            return True
        else:
            return self.current_time <= self.end_time

    async def sleep(self, seconds: float):
        """지정된 시간만큼 대기합니다.

        Args:
            seconds (float): 대기할 시간(초)

        Note:
            - 실시간 모드: asyncio.sleep을 사용하여 실제로 대기
            - 백테스팅 모드: 가상 시간을 진행하고 콜백 함수 호출
                1. on_before_time_change 콜백 호출 (설정된 경우)
                2. 현재 시간 업데이트
                3. on_time_change 콜백 호출 (설정된 경우)
        """
        if self.live_mode:
            await asyncio.sleep(seconds)
        else:
            before = self.current_time
            after = before + dtm.timedelta(seconds=seconds)

            if self.on_before_time_change:
                self.on_before_time_change(before, after)

            self.current_time = after

            if self.on_time_change:
                self.on_time_change(self.current_time, before)
