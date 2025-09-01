from enum import Enum
from pyqqq.backtest.wallclock import WallClock
from typing import Optional, TextIO
import datetime as dtm
import sys
import traceback


class LogLevel(Enum):
    """로그 레벨을 정의하는 열거형 클래스"""

    DEBUG = ("D", 10)  # Debug level
    INFO = ("I", 20)  # Info level
    WARNING = ("W", 30)  # Warning level
    ERROR = ("E", 40)  # Error level

    def __init__(self, symbol: str, level_value: int):
        self._symbol = symbol
        self._level_value = level_value

    @property
    def symbol(self) -> str:
        """로그 레벨 심볼을 반환합니다."""
        return self._symbol

    @property
    def level_value(self) -> int:
        """로그 레벨 값을 반환합니다."""
        return self._level_value


class Logger:
    """백테스트와 실시간 거래에서 모두 사용할 수 있는 커스텀 로거"""

    def __init__(self, name: str, wall_clock: Optional[WallClock] = None, level: LogLevel = LogLevel.INFO, output: Optional[TextIO] = None, error_output: Optional[TextIO] = None):
        self.name = name
        self.level = level
        self.wall_clock = wall_clock
        self.output = output or sys.stdout
        self.error_output = error_output or sys.stderr

    def _should_log(self, level: LogLevel) -> bool:
        """주어진 레벨의 로그를 출력해야 하는지 확인합니다."""
        return level.level_value >= self.level.level_value

    def _get_timestamp(self) -> str:
        """현재 시간 문자열을 반환합니다."""
        if self.wall_clock is None:
            now = dtm.datetime.now()
        else:
            now = self.wall_clock.now()
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def _write(self, level: LogLevel, message: str, output: TextIO = None):
        """로그 메시지를 작성합니다."""
        if not self._should_log(level):
            return

        output = output or self.output
        timestamp = self._get_timestamp()
        log_line = f"{timestamp} {level.symbol} {self.name}: {message}\n"
        output.write(log_line)
        output.flush()

    def set_level(self, level: LogLevel):
        """로그 레벨을 설정합니다."""
        self.level = level

    def debug(self, message: str):
        """디버그 레벨 로그를 출력합니다."""
        self._write(LogLevel.DEBUG, message)

    def info(self, message: str):
        """정보 레벨 로그를 출력합니다."""
        self._write(LogLevel.INFO, message)

    def warning(self, message: str):
        """경고 레벨 로그를 출력합니다."""
        self._write(LogLevel.WARNING, message)

    def error(self, message: str):
        """에러 레벨 로그를 출력합니다."""
        self._write(LogLevel.ERROR, message, self.error_output)

    def exception(self, message: str):
        """현재 예외의 스택 트레이스와 함께 에러 레벨 로그를 출력합니다."""
        exc_info = traceback.format_exc()
        full_message = f"{message}\n{exc_info}"
        self._write(LogLevel.ERROR, full_message, self.error_output)


def get_logger(name: str, wall_clock, level: LogLevel = LogLevel.DEBUG) -> Logger:
    """로거 인스턴스를 생성합니다."""
    return Logger(name, wall_clock, level)
