# -*- coding:utf-8 -*-

"""
File Name : 'consumer'.py
Description: 消息队列消费者
Author: 'qinyuchen'
Date: '18-3-6' '下午5:19'
"""
import json
import shutil
from mq_consumer import Consumer
import time
import re
from creat_log import creat_app_log
from down_wav import WavDown
from pretty_log import pretty_print
from redis_pool import RedisPool
from threading import Timer
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import  ThreadPoolExecutor


RABBITMQ_HOST = "127.0.0.1"
RABBITMQ_USER = "admin"
RABBITMQ_PWD = "guiji@123qwe"
QUQUE_NAME = "download"
REQ_TIMEOUT = 20         # 超时时间
consumer_logger = creat_app_log('/home/log_sellbot/audio-download/')

def handle_info(session_info):
    """
    消费者  回调函数---主入口
    :param session_info:
    :return:
    """
    consumer_logger.info("begin to run handle_info")
    # MQ 中返回的是 bytes 类型 ，所以加了decode
    session_info = session_info.decode('utf-8')
    content = eval(session_info)
    consumer_logger.info("received msg:{} from MQ".format(pretty_print(content)))
    if content is None:
        consumer_logger.info("received None")
        return 1
    # 任务id
    id = content['task_id']
    # 下载url列表
    # filenamelist = re.findall("http://\S+.wav", str(content['download']))
    filenamelist = content['download']
    consumer_logger.info("filenamelist type:{}".format(str(type(filenamelist))))

    # 通知前端的url
    callback_url = content['url']
    try:
        consumer_logger.info("WavDown start! ")
        down_wav_object = WavDown(id, filenamelist, callback_url, consumer_logger)
        res_json = down_wav_object.run()
        consumer_logger.info("WavDown done! {}".format(pretty_print(res_json)))
        consumer_logger.info("WavDown finish, begin to notify download_url !")
        down_wav_object.notify_schedule(send_json_schedule=res_json)
        consumer_logger.info("WavDown finish, end  notify download_url ! {}".format(pretty_print(res_json)))
        return 1
    except Exception as e:
        consumer_logger.error("WavDown error! error info:\n{}".format(str(e)))
        return 1

def main():
    rs = RedisPool()
    r, pool = rs.redis_init()
    consumer_logger.info("init redis object")
    executor = ThreadPoolExecutor(max_workers=5)
    r_list = r.keys()
    consumer_logger.info("begin to get  redis keys {}".format(r_list))
    # print(r_list)
    sort_r_list = sorted(r_list, key=lambda x: x[-5:])

    for key in sort_r_list:
        item_session_info = r.get(key)
        consumer_logger.debug("begin to headle MSG {}".format(item_session_info.decode()))
        executor.submit(handle_info, item_session_info)

    consumer_logger.info("end to get  redis keys {}".format(r_list))
    executor.shutdown(wait=True)

    consumer_logger.info("all reids MSG has been done finnish")

    consumer_logger.info("begin to delete reids MSG")
    for key in r_list:
        r.delete(key)
    consumer_logger.info("end to delete reids MSG")
    rs.redis_close(pool)

    t = Timer(interval=15, function=main)
    t.start()

if __name__ == '__main__':
    main()