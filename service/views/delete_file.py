from flask import Blueprint
from flask import request
from flask import jsonify
from flask_restful import Resource
from flask import current_app
import requests
import os
import json

delete_file_entry = Blueprint('delete_file', __name__)


# 删除文件接口
class DeleteFile(Resource):
    def post(self):
        logger = current_app.app_logger
        content = request.get_json()
        logger.info(content)
        # 获取文件路径并删除文件
        old_filename = content['url']
        file_name = os.path.split(old_filename)[-1]
        file_path = '/usr/local/src/download/' + str(file_name)
        try:
            os.remove(file_path)
            logger.info("delete file {}".format(file_path))
            return jsonify({"status": "ok"})
        except Exception as e:
            logger.error("can't delete file error info: {}".format(str(e)))
            # 如果文件不存在说明删除,返回值ok
            if str(e) == "[Errno 2] No such file or directory":
                return jsonify({"status": "ok"})
            return jsonify({"status": "error"})


if __name__ == "__main__":
    url = 'http://localhost:9000/files'
    headers = {
        'content-type': 'application/json'
    }
    data = {
        'task_id': '6666'
    }
    res = requests.post(url, headers=headers, data=json.dumps(data))
    print(res.content.decode('utf-8'))
