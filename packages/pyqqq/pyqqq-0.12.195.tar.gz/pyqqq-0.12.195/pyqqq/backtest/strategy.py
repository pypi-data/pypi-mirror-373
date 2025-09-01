from pyqqq.backtest.broker import BaseBroker
from pyqqq.backtest.environment import TradingEnvironment
from pyqqq.backtest.logger import Logger, get_logger
from pyqqq.backtest.wallclock import WallClock


class BaseStrategy:
    """트레이딩 전략을 구현하기 위한 추상 기본 클래스입니다.

    이 클래스는 모든 트레이딩 전략의 기본이 되는 추상 클래스로,
    전략 구현에 필요한 기본적인 컴포넌트들을 제공합니다.
    구체적인 트레이딩 전략은 이 클래스를 상속받아 구현해야 합니다.

    Example:

    .. highlight:: python
    .. code-block:: python

        class MyStrategy(BaseStrategy):
            async def run(self):
                while self.clock.is_alive():
                    # 시장 데이터 수집
                    data = self.broker.get_price("005930")

                    # 전략 로직 실행
                    if self._should_buy(data):
                        self.broker.create_order(
                            "005930",
                            OrderSide.BUY,
                            quantity=10
                        )
                        self.logger.info("Buy order created")

                    # 일정 시간 대기
                    await self.clock.sleep(60)

        # 전략 실행
        env = BacktestEnvironment(
            start_time=datetime(2024, 10, 2, 9, 0),
            end_time=datetime(2024, 10, 21)
        )

        strategy = MyStrategy(env)
        await strategy.run()
    """

    clock: WallClock
    """ 시간 관리를 담당하는 시계 인스턴스 """
    broker: BaseBroker
    """ 거래 실행을 담당하는 브로커 인스턴스 """
    logger: Logger
    """ 로깅을 담당하는 로거 인스턴스 """

    def __init__(self, environment: TradingEnvironment):
        """BaseStrategy 클래스를 초기화합니다.

        Args:
            environment (TradingEnvironment): 트레이딩 환경 객체.
                실시간 거래 환경이나 백테스팅 환경이 될 수 있습니다.
                환경 객체로부터 시계, 브로커, 로거 인스턴스를 초기화합니다.

        Note:
            - environment 객체에서 다음 컴포넌트들을 초기화합니다:
                1. clock: 시간 관리 컴포넌트
                2. broker: 거래 실행 컴포넌트
                3. logger: 로깅 컴포넌트 (클래스 이름으로 자동 생성)
            - 실시간/백테스트 환경 모두에서 동일한 인터페이스 제공
        """
        self.clock = environment.get_clock()
        self.broker = environment.get_broker()
        self.logger = get_logger(self.__class__.__name__, self.clock)

    async def run(self):
        """전략을 실행합니다.

        이 메서드는 반드시 하위 클래스에서 구현되어야 합니다.
        전략의 메인 로직을 이 메서드에 구현하며, 일반적으로 다음과 같은
        작업들이 포함됩니다:
        - 시장 데이터 수집
        - 전략 로직 실행
        - 주문 생성 및 관리
        - 포지션 관리

        Raises:
            NotImplementedError: 이 메서드는 반드시 하위 클래스에서 구현되어야 합니다.

        Note:
            - 비동기(async) 메서드로 구현되어야 합니다.
            - clock.is_alive()를 통해 전략 실행 지속 여부를 확인할 수 있습니다.
            - clock.sleep()을 사용하여 적절한 간격으로 전략을 실행해야 합니다.
        """
        raise NotImplementedError
