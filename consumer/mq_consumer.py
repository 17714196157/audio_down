# -*- coding:utf-8 -*-
"""
File Name : 'mq_consumer'.py
Description:
Author: 'btows'
Date: '18-1-11' '下午2:16'
"""
"""
File Name : 'publish'.py
Description:
Author: 'btows'
Date: '18-1-11' '上午11:10'
"""
import logging
import pika


class Consumer:
    def __init__(self, host, username, password, queue_name, handle_data=None):
        self._params = pika.connection.ConnectionParameters(host=host,
                                                            virtual_host='/',
                                                            credentials=pika.credentials.PlainCredentials(username, password),
                                                            heartbeat_interval=600,
                                                            blocked_connection_timeout=300)
        self._conn = None
        self._channel = None
        self.queue_name = queue_name
        self.handle_data = handle_data

    def connect(self):
        if not self._conn or self._conn.is_closed:
            # 连接到rabbitmq服务器 ，创建链接
            self._conn = pika.BlockingConnection(self._params)
            # 创建一个通道
            self._channel = self._conn.channel()
            # 声明消息队列，消息将在这个队列中进行传递。如果队列不存在，则创建
            # durable 表示 队列持久化存储，exclusive是否排他，如果为True则只允许创建这个队列的消费者使用， auto_delete 表示消费完是否删除队列
            self._channel.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False)

    def callback(self, ch, method, properties, body):
        """
        回调函数，其中handle_data为处理接收到的消息，处理正确返回1，如果返回1，那么发送消息确认
        :param ch:和rabbitmq通信的信道
        :param method:一个方法帧对象
        :param properties:表示消息头对象
        :param body:消息内容
        :return:
        """
        print(" [x] Received %r" % (body.decode('utf-8')))
        result = self.handle_data(body)
        print("result:{}" .format(result))
        if result == 1:
            print(" [x] Done")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(" [x] handle data error")
            ch.basic_reject(delivery_tag=method.delivery_tag)

    def receive_message(self):
        """
        ###消费者启动的主函数#####

        接收消息队列中的消息, 并调用回调函数处理
        """
        # 同一时刻，不要发送超过一个消息到消费者，直到它已经处理完了上一条消息并作出了回应
        self._channel.basic_qos(prefetch_count=1)
        # 告诉rabbitmq使用callback来接收信息  queue_name 是队列名
        self._channel.basic_consume(self.callback, queue=self.queue_name)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            # channel.start_consuming() 开始接收信息，并进入阻塞状态，队列里有信息才会调用callback进行处理。按ctrl+c退出。
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self.close()

    def _publish(self, msg):
        self._channel.basic_publish(exchange='', routing_key=self.queue_name,
                                    body=msg, properties=pika.BasicProperties(delivery_mode=2))   # 使消息或任务也持久化存储
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
