import flask

from pika import BlockingConnection, PlainCredentials, \
    ConnectionParameters, BasicProperties
from pika.exchange_type import ExchangeType


class RabbitMQ:

    def __init__(self):
        self.url = flask.current_app.config['VIGGOCORE_QUEUE_URL']
        self.port = flask.current_app.config['VIGGOCORE_QUEUE_PORT']
        self.virtual_host = \
            flask.current_app.config['VIGGOCORE_QUEUE_VIRTUAL_HOST']
        self.username = flask.current_app.config['VIGGOCORE_QUEUE_USERNAME']
        self.password = flask.current_app.config['VIGGOCORE_QUEUE_PASSWORD']
        credentials = PlainCredentials(self.username, self.password)
        self.params = ConnectionParameters(
            self.url, self.port, self.virtual_host, credentials, heartbeat=60,
            blocked_connection_timeout=30, socket_timeout=None, retry_delay=10,
            connection_attempts=10000)

    def connect(self):
        try:
            return BlockingConnection(self.params)
        except Exception:
            raise


class BasicQueueConsumer():

    queue_name = None
    arguments = None
    exchanges = []

    def __init__(self, queue_name, exchanges=None, prefetch_size=None,
                 arguments=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        rabbitmq = RabbitMQ()
        self.connection = rabbitmq.connect()
        self.channel = self.connection.channel()
        if prefetch_size is not None:
            self.channel.basic_qos(prefetch_count=prefetch_size)
        self.queue_name = queue_name
        self.arguments = arguments
        self.exchanges = exchanges

    def __bind_queue(self):
        for ex in self.exchanges:
            exchange = ex.get('exchange', '')
            rounting_key = ex.get('routing_key', '')
            ex_type = ex.get('type', 'direct')
            self.channel.exchange_declare(exchange=exchange,
                                          exchange_type=ExchangeType[ex_type],
                                          durable=True)

            self.channel.queue_bind(self.queue_name, exchange=exchange,
                                    routing_key=rounting_key)

    def declare_and_consume(self, callback):
        self.channel.queue_declare(queue=self.queue_name, durable=True,
                                   arguments=self.arguments)
        self.channel.basic_consume(queue=self.queue_name, auto_ack=False,
                                   on_message_callback=callback)
        self.__bind_queue()

        self.channel.start_consuming()

    def close(self):
        self.channel.stop_consuming()
        self.channel.close()
        self.connection.close()

    def count_rejects_this_message(self, properties):
        count = 0
        xdeath = properties.headers.get('x-death', [])
        if len(xdeath) > 0:
            count = xdeath[0].get('count', 0)
        return count


class ProducerQueue:

    def __init__(self):
        rabbitmq = RabbitMQ()
        self.connection = rabbitmq.connect()
        self.channel = self.connection.channel()

    def publish(self, exchange, routing_key, body, properties=None):
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body,
                                   properties=properties)

    def _publish_entity(self, exchange, routing_key, body,
                        type, priority=None, headers=None):
        properties = BasicProperties(
            type=type, headers=headers, priority=priority)
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body,
                                   properties=properties)

    def publish_full_entity(self, exchange, routing_key, body,
                            type, priority):
        headers = {'event_type': 'FULL_ENTITY'}
        self._publish_entity(exchange, routing_key, body,
                             type, priority, headers)

    def publish_request_entity(self, exchange, routing_key, body,
                               type, priority):
        headers = {'event_type': 'REQUEST_ENTITY'}
        self._publish_entity(exchange, routing_key, body,
                             type, priority, headers)

    def publish_partial_entity(self, exchange, routing_key, body,
                               type, priority, event_name):
        headers = {'event_type': 'PARTIAL_ENTITY', 'event_name': event_name}
        self._publish_entity(exchange, routing_key, body,
                             type, priority, headers)

    def run(self, fn, *args):
        fn(self, *args)
        self.close()

    def close(self):
        self.channel.close()
        self.connection.close()
