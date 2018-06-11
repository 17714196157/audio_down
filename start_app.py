from flask import Flask
from flask_restful import Api
from service.views.get_download_info import download_info_entry
from service.views.delete_file import delete_file_entry
from service.views.hallo_world import hallo_entry
from service.views.get_download_info import DownloadInfo
from service.views.delete_file import DeleteFile
from service.views.hallo_world import Hallo
from service.creat_log import creat_app_log
from service.redis_pool import redis_init
import argparse
import os

# rabbitmq消息队列
RABBITMQ_HOST = "127.0.0.1"
RABBITMQ_USER = "admin"
RABBITMQ_PWD = "guiji@123qwe"
QUQUE_NAME = "download"


def creat_app():
    app = Flask(__name__)
    # 提交下载信息接口
    app.register_blueprint(download_info_entry)
    # 删除文件接口
    app.register_blueprint(delete_file_entry)
    app.register_blueprint(hallo_entry)
    view = Api(app)
    view.add_resource(DownloadInfo, '/download/info')
    view.add_resource(DeleteFile, '/download/files')
    view.add_resource(Hallo, '/download/hallo')
    return app


if __name__ == "__main__":
    # 命令行解析,默认服务启动端口10000
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=10000, help='main service port', type=int)
    parser.add_argument('-d', '--debug_mode', action="store_true")
    args = parser.parse_args()

    app = creat_app()
    with app.app_context():
        app.app_logger = creat_app_log()
        # 连接redis
        app.r, app.pool = redis_init()

    if args.debug_mode:
        print('app starting on debug mode')
        app.run('0.0.0.0', port=args.port, debug=True, threaded=True)
    else:
        print('app running, work dir is:', os.getcwd())
        app.run('0.0.0.0', port=args.port, threaded=True, debug=True)
