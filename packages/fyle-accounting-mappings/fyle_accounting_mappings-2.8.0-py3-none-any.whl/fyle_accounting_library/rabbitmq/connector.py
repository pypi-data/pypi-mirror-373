import os
import json
import logging

from common.qconnector import QConnector
from common.qconnector import RabbitMQConnector
from .data_class import RabbitMQData

logger = logging.getLogger(__name__)


class RabbitMQ(RabbitMQConnector):
    def __init__(self, rabbitmq_exchange: str):
        rabbitmq_url = os.environ.get('RABBITMQ_URL')
        self.qconnector: QConnector = RabbitMQConnector(rabbitmq_url, rabbitmq_exchange)
        self.qconnector.connect()

    def publish(self, routing_key, body: RabbitMQData):
        self.qconnector.publish(routing_key, body.to_json())

    def is_connected(self):
        try:
            return self.qconnector.channel.is_open
        except Exception:
            return False

    def ensure_connection(self):
        """Ensures the connection is active, reconnects if needed"""
        if not self.is_connected():
            self.qconnector.connect()


class RabbitMQConnection:
    _instance = None

    @classmethod
    def get_instance(cls, exchange_name):
        if cls._instance is None or not cls._instance.is_connected():
            cls._instance = cls._create_connection(exchange_name)
        return cls._instance

    @classmethod
    def _create_connection(cls, exchange_name):
        instance = RabbitMQ(exchange_name)
        return instance

    def publish(self, routing_key, payload):
        """Wrapper around publish to ensure connection is healthy"""
        try:
            self.ensure_connection()
            return super().publish(routing_key, payload)
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            # Optionally retry or raise the exception
            raise
