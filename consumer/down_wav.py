# -*- coding:utf-8 -*-

"""
File Name : 'consumer'.py
Description: 消息队列消费者
Author: 'qinyuchen'
Date: '18-3-6' '下午5:19'
"""
import hashlib
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import shutil
import requests
from creat_log import creat_app_log
import re

# todo 编码规范
# todo print改为logger


class WavDownBasic():
    # 共享录音打包文件夹 路径
    share_path = r"/usr/local/src/download"
    # 并发下载录音的线程数
    PoolNum = 10
    LocalPort = 10001
    # domain_name = "down.btows.com"
    domain_name = "192.168.1.52"


class WavDown(WavDownBasic):
    def __init__(self, seqid, list_wav_url, callback_url, consumer_logger):
        # 创建线程池
        self.executor = ThreadPoolExecutor(WavDownBasic.PoolNum)
        self.consumer_logger = consumer_logger
        # 批次号，在消息队列里获取
        self.seqid = seqid
        self.list_wav_url = list_wav_url
        self.callback_url = callback_url
        # todo 文件夹加时间戳

        # 创建md5对象
        m = hashlib.md5()
        m.update((str(self.seqid)+str(time.time())).encode())
        self.filename = m.hexdigest()
        # 创建一个下载文件夹暂存文件
        self.download_temppath = os.path.join(WavDownBasic.share_path, str(self.filename))

        self.consumer_logger.info("下载文件夹暂存文件 {}".format(self.download_temppath))
        self.consumer_logger.info("创建打包文件名 {}".format(self.filename))
        os.makedirs(self.download_temppath, exist_ok=True)

    def run(self):
        """
         主执行函数，执行批量下载 并打包
        :param list_Wav_url:  下载url列表
        :return res_json: 返回打包zip文件全路径
        """
        print("@@@@@@@@@@@@@@@@@@@@@@run ", self.list_wav_url)
        future_list = []
        for urlnode in self.list_wav_url:
            url = urlnode.strip()
            name = urlnode.split("/")[-1]
            res_flag = re.match('http', url)
            if res_flag is not None:
                future = self.executor.submit(self.do_down_wav, url, name)
            else:
                future = self.executor.submit(self.do_copy_wav, url, name)
            future_list.append(future)
        all_n = len(future_list)
        n = 0
        while n != all_n:
            n = 0
            for future in future_list:
                if future.done():
                    n = n+1
            time.sleep(3)
            schedule = int(n*100/all_n)
            self.consumer_logger.info("schedule {}".format(schedule))
            # 返回结果放在一个字典中
            res_json_schedule = {
                "task_id": str(self.seqid),
                "download": "",
                "schedule": str(schedule)
            }
            # todo 结果检验，异常处理
            if n != all_n:
                self.notify_schedule(send_json_schedule=res_json_schedule)
        self.executor.shutdown()

        self.consumer_logger.info('''begin make_archive  {}'''.format(self.download_temppath))
        t1 = time.time()
        # 第一个参数是归档文件名称，第二个参数是指定的格式，不仅是支持zip，第三个参数是要压缩文件/文件夹的路径
        # shutil.make_archive(os.path.join(WavDownBasic.share_path, self.filename), 'zip', self.download_temppath)
        self.consumer_logger.info('''zip -r -q -o {zippath} {download_temppath}'''.format(
            zippath=os.path.join(WavDownBasic.share_path, self.filename+".zip "),
            download_temppath=self.download_temppath))

        subprocess.run('''zip -r  -q -o {zippath}  {download_temppath}'''.format(
            zippath=os.path.join(WavDownBasic.share_path, self.filename+".zip"),
            download_temppath=self.download_temppath),
            shell=True, cwd=WavDownBasic.share_path)
        t2 = time.time()
        self.consumer_logger.debug('''end make_archive  {download_temppath} ,cost time {costtime}'''.format(download_temppath=self.download_temppath, costtime=(t2-t1)/60))

        t1 = time.time()
        # 删除暂存文件夹
        time.sleep(1)
        self.consumer_logger.debug('''begin del  {}'''.format(self.download_temppath))
        # shutil.rmtree(self.download_temppath, ignore_errors=True)
        subprocess.run('''rm -rf {download_temppath}'''.format(download_temppath=self.download_temppath),
                       shell=True, cwd=WavDownBasic.share_path)
        t2 = time.time()
        self.consumer_logger.debug('''end del  {download_temppath} ,cost time {costtime}'''.format(
            download_temppath=self.download_temppath, costtime=(t2 - t1) / 60))

        download_url = "http://{domain_name}:{LocalPort}/{filename}".format(domain_name=WavDownBasic.domain_name,
                                                                            LocalPort=WavDownBasic.LocalPort,
                                                                            filename=self.filename + ".zip")
        self.consumer_logger.info("task_id: {task_id} download_url: {download_url}".format(task_id=self.seqid,
                                                                                           download_url=download_url))
        # 返回结果放在一个字典中
        res_json = {
            "task_id": str(self.seqid),
            "download": str(download_url),
            "schedule": "100"
        }
        return res_json

    def do_down_wav(self, url, name):
        """
        下载单个网络上录音文件
        :param url:
        :param name:
        :return:
        """

        # print("下载地址为：",url,"文件名为：",name)
        try:
            self.consumer_logger.debug("begin download wav {url} {name}".format(url=url,name=name))
            res = requests.get(url=url)
            if res.status_code == 200:
                self.consumer_logger.debug("begin write wav {name} to localfile".format(url=url, name=name))
                with open(os.path.join(self.download_temppath,name), mode='bw') as f:
                    f.write(res.content)
                self.consumer_logger.debug("end write wav {name} to localfile".format(url=url, name=name))
            else:
                self.consumer_logger.error("[ERROR],wav文件下载异常，可能找不到 wav文件 {}".format(url))
        except Exception as e:
            self.consumer_logger.error("[ERROR],wav文件下载异常，可能无法访问 远程服务器{e} {url}".format(e=str(e),
                                                                                        url=str(url)))

    def do_copy_wav(self, filepath, name):
        """
        下载单个网络上录音文件
        :param url:
        :param name:
        :return:
        """
        des_path = os.path.join(self.download_temppath, name)
        sou_path = filepath
        if os.path.exists(sou_path):
            print("sou_path为：", sou_path, "des_path 为：", des_path)
            try:
                self.consumer_logger.debug("begin copy wav {filepath} {name}".format(filepath=filepath, name=name))
                shutil.copy(sou_path, des_path)
            except Exception as e:
                self.consumer_logger.error("[ERROR], wav文件copy异常，可能无法访问 远程服务器{}".format(str(e)))
        else:
            self.consumer_logger.error("[ERROR], wav文件copy异常，文件不存在")


    def notify_schedule(self, send_json_schedule):
        """
        发生进度情况给 回调通知地址
        :param send_json_schedule: 需要发生的消息体 json  Post请求
        :return:
        """
        try:
            res = requests.post(url=self.callback_url, json=send_json_schedule)
            res_content_json = json.loads(res.text)
            self.consumer_logger.debug("schedule notify code = {}".format(res_content_json['code']))
            if int(res_content_json['code']) != 1:
                self.consumer_logger.error("schedule notify error! {}".format(res_content_json['msg']))
            else:
                self.consumer_logger.debug("schedule notify OK! {}".format(res_content_json['msg']))
        except Exception as e:
            self.consumer_logger.error("schedule notify error! Network anomaly  {}".format(str(e)))


def test():
    """
    测试代码
    :return:
    """
    from creat_log import creat_app_log
    WavDownBasic.share_path = r"/usr/local/src/download/"
    consumer_logger = creat_app_log('/home/log_sellbot/audio-download/')
    with open(r"/usr/local/src/audio-download/consumer/rabbimq_message.json", mode='r') as f:
        request_data = json.load(f)
        id = request_data['task_id']
        filenamelist = request_data['download']
        callback_url = request_data['url']
        down_wav_object = WavDown(id, filenamelist, callback_url, consumer_logger)
        res_json = down_wav_object.run()
        down_wav_object.notify_schedule(send_json_schedule=res_json)


if __name__ == "__main__":
    test()
