from dotenv import load_dotenv
from pyqqq.brokerage.ebest.simple import EBestSimpleDomesticStock
from pyqqq.brokerage.kis.simple import KISSimpleDomesticStock
from pyqqq.datatypes import *
from pyqqq.utils.kvstore import KVStore
from pyqqq.utils.logger import get_logger
from pyqqq.brokerage.tracker import TradingTracker


load_dotenv()


class PositionClassifier:
    """주문, 포지션의 주체를 분류하기 위한 클래스입니다.

    자동 거래 프로그램에서 사용중인 계좌로 직접 HTS, MTS 등으로 거래를 하는 유저를 위해 만들어진 분류기 입니다.
    """

    logger = get_logger(__name__ + ".PositionClassifier")

    DEF_DIRECT_POSITION_KEY = "direct_position"
    DEF_DIRECT_ORDER_KEY = "direct_order"
    DEF_AUTO_POSITION_KEY = "auto_position"
    DEF_AUTO_ORDER_KEY = "auto_order"
    DEF_TAG_AUTO_ORDER_KEY = "tag_auto_order"

    def __init__(
        self,
        simple_data_api: EBestSimpleDomesticStock | KISSimpleDomesticStock,
        kv_store_collection,
        default_type="auto",
    ):
        """OrderClassifier 초기화 메서드입니다

        Args:
            data_api (KISSimpleDomesticStock):
                시세 조회 및 시장 데이터 조회를 위한 API 인터페이스
            kv_store_collection (String):
                kv_store에서 사용할 콜렉션
            default_type (String):
                태깅되지 않은 종목을 무엇으로 간주할지.
                'auto', 'direct' 둘 중 한 값을 가짐

        Note:
            생성된 인스턴스는 즉시 거래가 가능한 상태가 되며,
            모든 거래 관련 작업은 자동으로 로깅됩니다.

        """

        # key: asset_code(str), value: quantity(int)
        self.auto_positions = {}
        self.direct_positions = {}

        # key: order_no(str), value: remain_quantity(int)
        self.auto_pending_orders = {}
        self.direct_pending_orders = {}

        # list of order_no(str)
        self.tagged_auto_pending_orders = []

        self.kv_store = KVStore(kv_store_collection)
        self.api = simple_data_api

        if default_type in ['auto', 'direct']:
            self.default_type = default_type
        else:
            self.default_type = 'auto'

        self.tracker = TradingTracker(simple_data_api)
        self.tracker.add_pending_order_update_callback(self._on_pending_order_update)

        self.set_initial_position()

    def set_initial_position(self) -> None:
        """코드 시작시 현재 account에 있는 position과 kv_store를 참고해서
        기존 포지션을 분류한다.
        Args:
        """
        cur_pos = self.api.get_positions()
        kv_auto_pos = self.kv_store.get(self.DEF_AUTO_POSITION_KEY) or {}
        kv_direct_pos = self.kv_store.get(self.DEF_DIRECT_POSITION_KEY) or {}

        self.logger.info(f"set_initial_position. kv_auto_pos: {kv_auto_pos}, kv_direct_pos: {kv_direct_pos}")
        for pos in cur_pos:
            asset_code = pos.asset_code
            quantity = pos.quantity

            if kv_auto_pos is not None and asset_code in kv_auto_pos:
                self.auto_positions[asset_code] = min([quantity, kv_auto_pos[asset_code]])
                quantity -= self.auto_positions[asset_code]
            if asset_code in kv_direct_pos:
                self.direct_positions[asset_code] = min(quantity, kv_direct_pos[asset_code])
                quantity -= self.direct_positions[asset_code]
            if quantity > 0:
                if self.default_type == "auto":
                    if asset_code in self.auto_positions:
                        self.auto_positions[asset_code] += quantity
                    else:
                        self.auto_positions[asset_code] = quantity
                elif self.default_type == "direct":
                    if asset_code in self.direct_positions:
                        self.direct_positions[asset_code] += quantity
                    else:
                        self.direct_positions[asset_code] = quantity

        self.update_positions()
        self.logger.info(f"set_initial_position.\npositions: {cur_pos}\nauto_positions: {self.auto_positions}\ndirect_positions: {self.direct_positions}")

    def set_initial_order(self):
        cur_order = self.api.get_pending_orders(exchanges=[OrderExchange.KRX, OrderExchange.NXT, OrderExchange.SOR])
        kv_auto_orders = self.kv_store.get(self.DEF_AUTO_ORDER_KEY) or {}
        kv_direct_orders = self.kv_store.get(self.DEF_DIRECT_ORDER_KEY) or {}
        kv_auto_tag_orders = self.kv_store.get(self.DEF_TAG_AUTO_ORDER_KEY) or []

        self.logger.info(f"set_initial_order. kv_auto_orders: {kv_auto_orders}, kv_direct_orders: {kv_direct_orders}")

        for order in cur_order:
            order_no = cur_order.order_no
            quantity = cur_order.pending_quantity

            if order_no in kv_auto_tag_orders:
                self.tagged_auto_pending_orders.append(order_no)

            if order_no in kv_auto_orders:
                self.auto_pending_orders[order_no] = min(quantity, kv_auto_orders[order_no])
            elif order_no in kv_direct_orders:
                self.direct_pending_orders[order_no] = min(quantity, kv_direct_orders[order_no])
            else:
                if self.default_type == "auto":
                    self.auto_pending_orders[order_no] = quantity
                elif self.default_type == "direct":
                    self.direct_pending_orders[order_no] = quantity

        self.update_orders()
        self.logger.info(f"set_initial_order.\orders: {cur_order} \nauto_pending_orders: {self.auto_pending_orders} \ndirect_pending_orders: {self.direct_pending_orders}")

    def update_positions(self) -> None:
        self.kv_store.set(self.DEF_AUTO_POSITION_KEY, self.auto_positions)
        self.kv_store.set(self.DEF_DIRECT_POSITION_KEY, self.direct_positions)

    def update_orders(self):
        self.kv_store.set(self.DEF_AUTO_ORDER_KEY, self.auto_pending_orders)
        self.kv_store.set(self.DEF_TAG_AUTO_ORDER_KEY, self.tagged_auto_pending_orders)
        self.kv_store.set(self.DEF_DIRECT_ORDER_KEY, self.direct_pending_orders)

    def clear_orders(self) -> None:
        """
        날 바뀌고 kv store에 남아있는 오더는 모두 유효지 않음
        장 시작 전에 호출해주면 좋은 함수
        """
        self.logger.info("clear_orders")
        self.auto_pending_orders = {}
        self.direct_pending_orders = {}
        self.tagged_auto_pending_orders = []
        self.update_orders()

    def get_sellable_quantity_by_auto(self, asset_code, quantity) -> int:
        """pyqqq로 매수했던 수량을 체크해서, 매도간에 pyqqq로 샀던게 몇 주인지 확인하는 함수

        Args:
            asset_code (String): 종목코드 6자리
            quantity (int): 체크 하려는 수량.
            만약 프로그램으로 5주, 손으로 5주 매수해서 10주 들고있는 상황에서 quantity가 8이면
            5를 return 한다.
        """
        ret = 0

        positions = self.api.get_positions()
        for position in positions:
            if asset_code == position.asset_code:
                remained = min(quantity, position.sell_possible_quantity)
                if asset_code in self.auto_positions:
                    diff = min(self.auto_positions[asset_code], remained)
                    ret += diff
                    remained -= diff

                if self.default_type == "auto":
                    if asset_code in self.direct_positions:
                        diff = min(self.direct_positions[asset_code], remained)
                        remained -= diff

                    ret += remained
                break
        return ret

    # 매수, 매도 할때 명시적으로 호출해줘야함
    def tagging_order_auto(self, order_no: str):
        self.logger.info(f"tagging_order_auto. order_no: {order_no}")
        if order_no in self.auto_pending_orders:
            self.logger.info(f"tagging_order_auto. {order_no} already exist")
            return

        elif order_no in self.direct_pending_orders:
            self.logger.info(f"tagging_order_auto. {order_no} has been in direct_pending_orders")
            self.auto_pending_orders[order_no] = self.direct_pending_orders[order_no]

            del self.direct_pending_orders[order_no]

        elif order_no not in self.tagged_auto_pending_orders:
            self.logger.info(f"tagging_order_auto. {order_no} is tagged.")
            self.tagged_auto_pending_orders.append(order_no)

        self.update_orders()

    def _on_pending_order_update(self, status, order: StockOrder):
        """Tracker를 통해
        TradingTracker의 add_pending_order_update_callback 함수에 인자로 넣으면 정상 동작함.
        """
        asset_code = order.asset_code
        order_no = order.order_no
        pending_quantity = order.pending_quantity

        self.logger.info(f"_on_pending_order_update. status: {status} order: {order}")

        # 주문 처리시
        if order.side == OrderSide.BUY:
            if status in ["partial", "completed"]:
                if order_no in self.auto_pending_orders:
                    prev_filled_quantity = order.quantity - self.auto_pending_orders[order_no]
                    filled_quantity = order.filled_quantity - prev_filled_quantity
                    self._add_dict_with_key(self.auto_pending_orders, order_no, -filled_quantity)
                    self._add_dict_with_key(self.auto_positions, asset_code, filled_quantity)

                elif order_no in self.direct_pending_orders:
                    prev_filled_quantity = order.quantity - self.direct_pending_orders[order_no]
                    filled_quantity = order.filled_quantity - prev_filled_quantity
                    self._add_dict_with_key(self.direct_pending_orders, order_no, -filled_quantity)
                    self._add_dict_with_key(self.direct_positions, asset_code, filled_quantity)

                elif order_no in self.tagged_auto_pending_orders or self.default_type == "auto":
                    self.auto_pending_orders[order_no] = pending_quantity
                    self._add_dict_with_key(self.auto_positions, asset_code, order.filled_quantity)

                elif self.default_type == "direct":
                    self.direct_pending_orders[order_no] = pending_quantity
                    self._add_dict_with_key(self.direct_positions, asset_code, order.filled_quantity)

            # 주문 접수시
            elif status in ["accepted"]:
                if order_no in self.tagged_auto_pending_orders:
                    self.auto_pending_orders[order_no] = order.pending_quantity
                else:
                    self.direct_pending_orders[order_no] = order.pending_quantity

            elif status in ["cancelled"]:
                if order_no in self.auto_pending_orders:
                    self.auto_pending_orders[order_no] -= order.quantity
                elif order_no in self.direct_pending_orders:
                    self.direct_pending_orders[order_no] -= order.quantity

        elif order.side == OrderSide.SELL:
            if status in ["accepted"]:
                # 매도시엔 보유 잔량을 주문 접수시 미리 차감한다.
                if order_no in self.tagged_auto_pending_orders:
                    self.auto_pending_orders[order_no] = pending_quantity

                    remain = self._add_dict_with_key(self.auto_positions, asset_code, -pending_quantity)

                    if remain < 0:
                        self._add_dict_with_key(self.direct_positions, asset_code, remain)

                else:
                    self.direct_pending_orders[order_no] = pending_quantity
                    remain = self._add_dict_with_key(self.direct_positions, asset_code, -pending_quantity)

                    if remain < 0:
                        self._add_dict_with_key(self.auto_positions, asset_code, remain)

            elif status in ["cancelled"]:
                # 주문 취소시엔 보유잔량을 복구한다.
                if order_no in self.auto_pending_orders:
                    # order.quantity가 주문 취소한 수량임
                    self.auto_pending_orders[order_no] -= order.quantity
                    self._add_dict_with_key(self.auto_positions, asset_code, order.quantity)
                elif order_no in self.direct_pending_orders:
                    self.direct_pending_orders[order_no] -= order.quantity
                    self._add_dict_with_key(self.direct_positions, asset_code, order.quantity)
            elif status in ["partial"]:
                # 부분 체결시엔 미체결분량으로 pending order 잔량을 업데이트한다.
                if order_no in self.auto_pending_orders:
                    self.auto_pending_orders[order_no] = pending_quantity
                elif order_no in self.direct_pending_orders:
                    self.direct_pending_orders[order_no] = pending_quantity
            elif status in ["completed"]:
                # 전체 체결시엔 메모리 정리를 위해 해당 주문번호를 비워준다. 진행하지 않아도 무방함
                if order_no in self.auto_pending_orders:
                    del self.auto_pending_orders[order_no]
                elif order_no in self.direct_pending_orders:
                    del self.direct_pending_orders[order_no]

        # clear
        self._clear_below_zero_key_value(self.auto_pending_orders, order_no)
        self._clear_below_zero_key_value(self.direct_pending_orders, order_no)
        self._clear_below_zero_key_value(self.auto_positions, asset_code)
        self._clear_below_zero_key_value(self.direct_positions, asset_code)

        self.update_orders()
        self.update_positions()

    def print_current_status(self):
        self.logger.info(
            f"print_current_status. auto positions: {self.auto_positions} direct positions: {self.direct_positions}.\nauto orders: {self.auto_pending_orders} direct_orders: {self.direct_pending_orders}.\n tagged order_nos: {self.tagged_auto_pending_orders}"
        )

    async def start(self):
        return await self.tracker.start()

    def _add_dict_with_key(self, target_dict, key, diff):
        """
        target dict가 비어있든 아니든 적절히 diff를 더해주는 연산.
        만약 연산 결과가 음수라면 그 음수값을 return하여 적절히 사용할 수 있도록 함
        """
        if key in target_dict:
            target_dict[key] += diff
        else:
            target_dict[key] = diff

        if target_dict[key] < 0:
            return target_dict[key]
        else:
            return 0

    def _clear_below_zero_key_value(self, target_dict, key):
        if key in target_dict and target_dict[key] <= 0:
            del target_dict[key]
