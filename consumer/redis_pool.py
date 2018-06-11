# -*- coding:utf-8 -*-

"""
File Name : 'redis_connect'.py
Description:
Author: 'chengwei'
Date: '2016/12/22' '17:30'
Version: '1.0'
"""

import redis

class RedisPool(object):
    def __init__(self):
        self.redis_host = '127.0.0.1'
        self.redis_port = 6379
        self.redis_db = '0'
        # self.redis_pwd = config.get('REDIS_PWD')

    def redis_init(self):
        """
        建立redis连接
        :return: 连接池
        """
        # pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=self.redis_db, password=self.redis_pwd)
        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        r = redis.StrictRedis(connection_pool=pool)
        return r, pool

    def redis_close(self, pool):
        """
        释放redis连接池
        :param pool:
        :return:
        """
        pool.disconnect()


if __name__ == '__main__':
    rs = RedisPool()
    r, pool = rs.redis_init()
    print("init")