import logging
import logging.handlers
import sys
from logging.handlers import TimedRotatingFileHandler

import pyqqq.config as c
from pyqqq.backtest.wallclock import WallClock

_default_format = "%(levelname).1s %(name)s: %(message)s"
if not c.is_google_cloud_logging_enabled():
    _default_format = "%(asctime)s " + _default_format


class CustomHandler(logging.StreamHandler):
    custom_format: str

    class ClockFormatter(logging.Formatter):
        def __init__(self, fmt=None, style="%", clock: WallClock = None):
            super().__init__(fmt, style)
            self.clock = clock or WallClock(live_mode=True)

        def formatTime(self, record, datefmt=None):
            dt = self.clock.now()
            return dt.isoformat(timespec="milliseconds")

    def __init__(self, stream):
        super().__init__(stream)
        self.custom_format = _default_format
        self.setFormatter(logging.Formatter(self.custom_format))

    def emit(self, record):
        super().emit(record)

    def update_format(self, format=None, clock: WallClock = None):
        if format:
            self.custom_format = format
        self.setFormatter(self.ClockFormatter(self.custom_format, clock=clock))


_stdout_h = CustomHandler(sys.stdout)
_stdout_h.setLevel(logging.DEBUG)
_stdout_h.addFilter(lambda r: r.levelno <= logging.WARNING)

_stderr_h = CustomHandler(sys.stderr)
_stderr_h.setLevel(logging.ERROR)

logging.basicConfig(handlers=[_stdout_h, _stderr_h])


def get_logger(
    name,
    level=logging.DEBUG,
    filename: str = None,
    when: str = "h",
    interval: int = 1,
    backup_count: int = 24,
) -> logging.Logger:
    """
    로깅을 위한 Logger 객체를 구성하고 반환합니다.

    이 함수는 주어진 이름과 세부 사항으로 Logger를 생성하고 설정합니다. 로그 파일 출력이 필요한 경우,
    파일 이름과 로테이션 정책(시간 간격 및 백업 수)을 지정할 수 있습니다. 로그는 지정된 레벨 또는 그 이상의 메시지만 기록합니다.

    Args:
        name (str): Logger의 이름.
        level (int, optional): 로깅 레벨. 기본값은 logging.DEBUG.
        filename (str, optional): 로그 파일의 이름. 지정하지 않으면 콘솔 로깅만 수행됩니다.
        when (str, optional): 로그 파일의 로테이션 주기 단위. 기본값은 'h'(시간).
        interval (int, optional): 로테이션 간격. 'when'에 지정된 단위에 따라 계산됩니다. 기본값은 1.
        backup_count (int, optional): 보관할 백업 파일의 최대 개수. 기본값은 24.

    Returns:
        logging.Logger: 구성된 로거 객체.

    Examples:
        >>> logger = get_logger('my_logger', filename='myapp.log')
        >>> logger.info('This is an info message')
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers and filename:
        fh = TimedRotatingFileHandler(filename, when=when, backupCount=backup_count, interval=interval)
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter(_default_format))
        logger.addHandler(fh)

    return logger


def get_bare_logger(
    name,
    level=logging.NOTSET,
) -> logging.Logger:
    """
    level을 지정하지 않으면 NOTSET으로 설정되는 로거를 반환하기 위해 사용됩니다.

    get_logger() 의 backward-compatible 버전으로써 기본 python logging의 hierarchy를 따라 level을 설정할 수 있습니다.
    """
    return get_logger(name, level)


def set_all_logger_level(level):
    """
    모든 로거의 로깅 레벨을 하나로 맞춘다.
    """
    if type(level) is str:
        level = logging._nameToLevel.get(level, logging.NOTSET)

    if level not in [
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    ]:
        raise ValueError("Invalid log level")

    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(level)


def set_module_logger_level(level, name="pyqqq"):
    """
    지정된 hierarchy의 모든 로거의 로깅 레벨을 하나로 맞춘다.
    """
    if type(level) is str:
        level = logging._nameToLevel.get(level, logging.NOTSET)

    if level not in [
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    ]:
        raise ValueError("Invalid log level")

    for logger_name in logging.root.manager.loggerDict:
        if logger_name == name or logger_name.startswith(f"{name}."):
            logging.getLogger(logger_name).setLevel(level)


def get_handlers():
    """
    CustomHandler 클래스의 인스턴스를 반환합니다.
    """
    return [h for h in logging.root.handlers if isinstance(h, CustomHandler)]
