from flask import Blueprint
from flask import request
from flask import jsonify
from flask_restful import Resource
from flask import current_app
import json
import requests
from service.redis_op import redis_record

download_info_entry = Blueprint('download_info', __name__)


# 提交下载信息接口
class DownloadInfo(Resource):
    def post(self):
        logger = current_app.app_logger
        content = request.get_json()
        logger.info(content)
        try:
            # 将提交信息添加到redis
            redis_record(content, current_app.r)
            logger.info("received message {}".format(json.dumps(content)))
            return jsonify({"status": "received"})
        except Exception as e:
            logger.error("can't send message error info: {}".format(str(e)))
            return jsonify({"status": "error"})


if __name__ == "__main__":
    url = 'http://localhost:10000/download/info'
    headers = {
        'content-type': 'application/json'
    }
    data = {
     "task_id": "2",
     "download": [
     "http:\/\/global.res.btows.com\/monitor\/2018\/03\/06\/force-13566401479-717-20180306-143129-1520317889.321216_2.wav",
     "http:\/\/global.res.btows.com\/monitor\/2018\/03\/06\/force-13615763703-718-20180306-143137-1520317897.321231_2.wav",
     "http:\/\/global.res.btows.com\/monitor\/2018\/03\/06\/force-18795851159-706-20180306-143148-1520317908.211_2.wav",
     "http:\/\/global.res.btows.com\/monitor\/2018\/03\/06\/force-18757277216-702-20180306-143146-1520317906.37725_2.wav"
     ],
     "url": "http:\/\/test.btows.com\/admin\/ajax\/notify_task_download_call_voice.php"
}
    res = requests.post(url, headers=headers, data=json.dumps(data))
    print(res.content.decode('utf-8'))