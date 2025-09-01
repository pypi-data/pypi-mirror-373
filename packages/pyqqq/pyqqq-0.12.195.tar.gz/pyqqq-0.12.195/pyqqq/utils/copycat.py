import os
import pickle
import time
from datetime import datetime
from typing import List
from dataclasses import dataclass

import pika
from pyqqq.datatypes import *
from pyqqq.utils.logger import get_logger


class RabbitmqPubSub:
    """
    RabbitMQ 의 Publish/Subscribe 패턴을 사용하기 위해 연결 후 채널을 생성, 관리하는 클래스이다.
    Publisher는 fanout type으로 exchange에 메시지를 브로드캐스팅하고, Subscriber는 해당 exchange에 바인딩된 각각의 queue에서 메시지를 받는다.
    """
    logger = get_logger(f'{__name__}.RabbitmqPubSub')

    def __init__(self, host=None):
        self.host = host
        self.connect()

    def __del__(self):
        # if self.exchange_name:
        #    self.delete_exchange()
        try:
            if self.rabbitmq and not self.rabbitmq.is_closed:
                self.rabbitmq.close()
        except Exception:
            pass

    def connect(self):
        while True:
            try:
                params = pika.ConnectionParameters(
                    host=self.host or os.getenv('RABBITMQ_HOST') or 'localhost',
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
                self.rabbitmq = pika.BlockingConnection(params)
                self.channel = self.rabbitmq.channel()
                return
            except Exception as e:
                self.logger.warning(f'Reconnecting to rabbitmq... : {e}')
                time.sleep(1)

    def declare_exchange(self, exchange_name):
        if not exchange_name:
            raise ValueError("Exchange name is required")

        self.exchange_name = exchange_name
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout') # fanout 은 broadcast 방식. 즉, 모든 큐에 메시지를 전달한다.

    def delete_exchange(self):
        if self.exchange_name:
            self.channel.exchange_delete(exchange=self.exchange_name)

    def declare_queue(self, queue_name):
        if not self.exchange_name:
            raise ValueError("Exchange name is not declared yet")

        result = self.channel.queue_declare(queue=queue_name, exclusive=False) # exclusive=True이면 종료 시 큐가 삭제되어 메시지를 받을 수 없음
        return result.method.queue

    def bind_queue(self, queue_name):
        if not self.exchange_name:
            raise ValueError("Exchange name is not declared yet")

        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)

    def unbind_queue(self, queue_name):
        if not self.exchange_name:
            raise ValueError("Exchange name is not declared yet")

        self.channel.queue_unbind(exchange=self.exchange_name, queue=queue_name)

    def delete_queue(self, queue_name):
        self.channel.queue_delete(queue=queue_name)

    def publish(self, message: str):
        """
        메시지를 발행한다.
        """
        if not self.rabbitmq or self.rabbitmq.is_closed:
            self.logger.warning('reconnecting...')
            self.connect()

        if not self.exchange_name:
            raise ValueError("Exchange name is not declared yet")

        try:
            self.channel.basic_publish(exchange=self.exchange_name, routing_key='', body=message)
        except pika.exceptions.StreamLostError:
            self.logger.warning('reconnect while publish...')
            time.sleep(1)
            self.rabbitmq = None
            self.publish(message=message)
        self.logger.info(f" [x] Sent : {message}")

    def run_subscribe(self, queue_name, on_message_callback):
        """
        메시지 구독을 시작한다. (CTRL+C로 종료)
        """
        if not self.rabbitmq or self.rabbitmq.is_closed:
            self.logger.warning('reconnecting...')
            self.connect()

        self.channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback, auto_ack=False) # auto_ack=True이면, 에러 등의 상황으로 프로그램 종료 시 이후 메시지들이 소실될 수 있음
        self.logger.info(f' [*] Waiting for messages in {queue_name}. To exit press CTRL+C')
        try:
            self.channel.start_consuming()
        except pika.exceptions.StreamLostError:
            self.logger.warning('reconnect while subscribing...')
            time.sleep(1)
            self.run_subscribe(queue_name, on_message_callback)
        except KeyboardInterrupt as e:
            self.channel.stop_consuming()
            self.logger.info(" [x] Stopped consuming")
            raise e


class CopyCatPublisher(RabbitmqPubSub):
    """
    메시지를 다수의 Subscriber가 받을 수 있도록 브로드캐스팅하는 Publisher이다.

    TODO:
        - [ ] 사용자 권한 설정 ex) subscriber는 exchange에 write할 수 없어야 함
        - [ ] exchange와 queue의 이름의 uniqueness를 보장해야 함
        - [ ] 수정 및 취소 건은 org_order_no 가 서로 일치하지 않으므로 다른 방법으로 따라하도록 수정해야 함
    """
    logger = get_logger(f'{__name__}.CopyCatPublisher')

    def __del__(self):
        # self.destroy()
        super().__del__()

    @classmethod
    def build(cls, exchange_name, queue_names=[], host=None):
        """
        하나의 주제(exchange_name)로 여러 개의 메시지 큐를 포함한 Publisher를 생성한다.
        각각의 메시지 큐는 독립적으로 메시지를 받아서 처리할 수 있다.
        """

        c = cls(host=host)
        c.declare_exchange(exchange_name)
        for q in queue_names:
            c.declare_queue(q)
        return c

    def destroy(self, queue_names=[]):
        for q in queue_names:
            self.unbind_queue(q)
            self.delete_queue(q)
        self.delete_exchange()

    def add_mq(self, queue_name):
        """
        Publisher에 새로운 메시지 큐를 추가한다.

        TODO: 이름 중복일 때?
        """

        self.declare_queue(queue_name)


class CopyCatSubscriber(RabbitmqPubSub):
    """
    Publisher가 발행한 이벤트 메시지를 받아서 순차적으로 모방할 수 있도록 도와주는 카피캣이다.
    """
    logger = get_logger(f'{__name__}.CopyCatSubscriber')

    def __init__(self, queue_name, host=None):
        super().__init__(host=host)
        self.queue_name = queue_name

    def __del__(self):
        # self.destroy()
        super().__del__()

    @classmethod
    def build(cls, exchange_name, queue_name, host=None):
        c = cls(queue_name, host=host)
        c.declare_exchange(exchange_name)
        c.bind_queue(queue_name)
        return c

    def destroy(self):
        if self.queue_name:
            self.unbind_queue(self.queue_name)
            self.delete_queue(self.queue_name)

    def run(self, on_message_callback=None):
        # on_message_callback 이 함수가 아니면 self._on_message 함수를 사용
        if not on_message_callback or not callable(on_message_callback):
            on_message_callback = self._on_message
        self.run_subscribe(self.queue_name, on_message_callback)

    def _on_message(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)

        message = pickle.loads(body)
        dt = message['dt']
        command = message['command']
        self.logger.info(f" [x] Received {command} at {dt.isoformat()}")
        data = message.get('order_form')
        if command == OrderRequestType.NEW or command == MessageType.OrderRequestNew:
            self.logger.info(f" [x] New order: {data}")
            # TODO: 따라하기
        elif command == OrderRequestType.MODIFY or command == MessageType.OrderRequestModify:
            self.logger.info(f" [x] Modify order: {data}")
            # TODO: 어떤 주문에서 내용을 수정할 것인지 알아내는 것은 쉽지 않다.
        elif command == OrderRequestType.CANCEL or command == MessageType.OrderRequestCancel:
            self.logger.info(f" [x] Cancel order: {data}")
            # TODO: 어떤 주문에서 취소할 것인지 알아내는 것은 쉽지 않다.
        elif command == MessageType.PositionsReport:
            data = message.get('positions', [])
            self.logger.info(f" [x] Total positions: {len(data)}")
            for position in data:
                self.logger.info(f" [x] {position}")
        else:
            self.logger.info(f" [x] Unknown command: {command}")


@dataclass
class OrderForm:
    asset_code: str
    status: TransactionStatus = None # 주문/체결 구분자
    side: OrderSide = None
    order_type: OrderType = None
    price: int = None
    quantity: int = None


@dataclass
class SimplePosition:
    asset_code: str
    asset_name: str
    quantity: int


class MessageType(Enum):
    OrderRequestNew = 1
    OrderRequestModify = 2
    OrderRequestCancel = 3
    PositionsReport = 4


class CopyCatMessage:
    @staticmethod
    def make_for_create(asset_code: str, status: TransactionStatus, side: OrderSide, order_type: OrderType, price: int = None, quantity: int = None):
        command = MessageType.OrderRequestNew
        status = status or TransactionStatus.ORDER
        order_form = OrderForm(asset_code=asset_code, status=status, side=side, order_type=order_type, price=price, quantity=quantity)
        return pickle.dumps({
            "dt": datetime.now(),
            "command": command,
            "order_form": order_form,
        })

    @staticmethod
    def make_for_update(asset_code: str, order_type: OrderType, price: int = None, quantity: int = None):
        command = MessageType.OrderRequestModify
        order_form = OrderForm(asset_code=asset_code, order_type=order_type, price=price, quantity=quantity)
        return pickle.dumps({
            "dt": datetime.now(),
            "command": command,
            "order_form": order_form,
        })

    @staticmethod
    def make_for_cancel(asset_code: str, quantity: int = None):
        command = MessageType.OrderRequestCancel
        order_form = OrderForm(asset_code=asset_code, quantity=quantity)
        return pickle.dumps({
            "dt": datetime.now(),
            "command": command,
            "order_form": order_form,
        })

    @staticmethod
    def make_for_positions(positions: List[StockPosition]):
        command = MessageType.PositionsReport
        results = []
        for position in positions:
            results.append(SimplePosition(asset_code=position.asset_code, asset_name=position.asset_name, quantity=position.quantity))
        return pickle.dumps({
            "dt": datetime.now(),
            "command": command,
            "positions": results,
        })

    @staticmethod
    def parse(message: str):
        return pickle.loads(message)
