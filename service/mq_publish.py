import logging
import pika


# 将提交的下载信息添加到rabbitmq
class Publisher:
    def __init__(self, host, username, password, queue_name):
        self._params = pika.connection.ConnectionParameters(host=host,
                                                            virtual_host='/',
                                                            credentials=pika.credentials.PlainCredentials(username, password))
        self._conn = None
        self._channel = None
        self.queue_name = queue_name

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            # durable 表示是否持久化，exclusive是否排他，如果为True则只允许创建这个队列的消费者使用， auto_delete 表示消费完是否删除队列
            self._channel.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False)

    def _publish(self, msg):
        self._channel.basic_publish(exchange='', routing_key=self.queue_name,
                                    body=msg, properties=pika.BasicProperties(delivery_mode=2))
        logging.info('message sent: %s', msg)

    def publish(self, msg):
        """Publish msg, reconnecting if necessary."""

        try:
            self._publish(msg)
        except pika.exceptions.ConnectionClosed:
            logging.debug('reconnecting to queue')
            self.connect()
            self._publish(msg)

    def close(self):
        if self._conn and self._conn.is_open:
            logging.debug('closing queue connection')
            self._conn.close()
