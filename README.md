已部署的机器：
124.192.16.139:50024   ----- 192.168.1.52

安装依赖包：
    yum install -y unzip zip
    yum install nginx
    pip install supervisor
    pip install pika
    pip install redis
方案一）
start_app.py  启动一个监听web服务器--------flask模块现实
              监听到外部批量下载请求，就将消息 写入 rabbitMQ


批量下载请求 json消息体如下
{
     "task_id": "2",
     "download": [
     "http://global.res.btows.com/monitor/2018/03/06/force-13566401479-717-20180306-143129-1520317889.321216_2.wav",
     "http://global.res.btows.com/monitor/2018/03/06/force-18795851159-706-20180306-143148-1520317908.211_2.wav",
     "http://global.res.btows.com/monitor/2018/03/06/force-18757277216-702-20180306-143146-1520317906.37725_2.wav",
       "http://asdglobal.res.btows.com/monitor/2018/03/06/force-18757277216-702-20180306-143146-1520317906.37725_2.wav"
     ],
     "url": "http://test.btows.com/admin/ajax/notify_task_download_call_voice.php"
}


consumer.py  启动消费者，消费者监听rabbitMQ ,多线程下载wav文件，并打包zip，存放在share_Path目录下
             下载过程中没3s 主动通知url 当前下载进展
			 下载完成后返回下载给通知回调地址url
	       {
                "task_id": str(self.seqid),
                "download": "",
                "schedule": str(schedule)
            }		 

启动ngnix服务 ，配置10001端口 监听下载zip包的请求， 配置10000端口 监听批量下载的post请求
                配置 每个IP 限速 200KB ，可以启动多个consumer
				

方案二）
start_app.py  启动一个监听web服务器--------flask模块现实
              监听到外部批量下载请求，就将消息 写入 redis数据库  

批量下载请求 json消息体如下
{
     "task_id": "2",
     "download": [
     "http://global.res.btows.com/monitor/2018/03/06/force-13566401479-717-20180306-143129-1520317889.321216_2.wav",
     "http://global.res.btows.com/monitor/2018/03/06/force-18795851159-706-20180306-143148-1520317908.211_2.wav",
     "http://global.res.btows.com/monitor/2018/03/06/force-18757277216-702-20180306-143146-1520317906.37725_2.wav",
       "http://asdglobal.res.btows.com/monitor/2018/03/06/force-18757277216-702-20180306-143146-1520317906.37725_2.wav"
     ],
     "url": "http://test.btows.com/admin/ajax/notify_task_download_call_voice.php"
}


consumer.py  启动消费者，消费者没15s 读取一次全部的redis数据，启动多个线程并发处理 ,多线程下载wav文件，并打包zip，存放在share_Path目录下
             下载过程中没3s 主动通知url 当前下载进展
			 下载完成后返回下载给通知回调地址url
	       {
                "task_id": str(self.seqid),
                "download": "",
                "schedule": str(schedule)
            }		 

启动ngnix服务 ，配置10001端口 监听下载zip包的请求， 配置10000端口 监听批量下载的post请求
                配置 每个IP 限速 200KB ，只可以启动一个consumer，防止 redis