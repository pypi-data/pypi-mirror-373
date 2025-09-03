import json
import logging
from typing import Any

import pika

from .abstract_domain_events_service import AbstractDomainEventsService
from ..domain import DomainEvent
from ..utils import config

class AMQPService(AbstractDomainEventsService):
    def __init__(self):
        self.rabbit_host = config('RABBIT.HOST')
        self.rabbit_port = config('RABBIT.PORT')
        self.credentials = pika.PlainCredentials(config('RABBIT.USER'), config('RABBIT.PASSWORD'))

    def publish(self, message: Any, event_type: DomainEvent, exchange: str = None):
        rabbit_exchange = exchange if not exchange is None else config('RABBIT.EXCHANGE')
        rabbit_default_routing_key = event_type if not event_type is None else config('RABBIT.DEFAULT_ROUTING_KEY')

        cnn = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host,
                                                                port=self.rabbit_port,
                                                                credentials=self.credentials))
        channel = cnn.channel()
        channel.exchange_declare(exchange=rabbit_exchange, exchange_type='direct', durable=True)

        message_body = json.dumps(message).encode('utf-8')

        channel.basic_publish(
            exchange=rabbit_exchange,
            routing_key=rabbit_default_routing_key,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent message
            ),
        )
        cnn.close()
        logging.getLogger('api').debug(f'Message sent to exchange {rabbit_exchange} using routing_key {rabbit_default_routing_key}')