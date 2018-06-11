# -*- coding:utf-8 -*-

"""
File Name : 'redis_op'.py
Description:
Author: 'btows'
Date: '18-1-8' '下午7:24'
"""
import json
import time


# key有效期1天，86400秒
def redis_expire(seqid, r):
    r.expire(seqid, 86400)


# redis添加数据
def redis_record(content, r):
    try:
        task_id = content['task_id']
        seqid = task_id + str(int(time.time()))
        r.set(seqid, content)
    except:
        raise Exception


# 查询redis是否有此会话记录
def query_redis_exist(seqid, r):
    if r.exists(seqid):
        return True
    else:
        return False


# 查询redis中此会话打断的状态
def query_redis_seqid(seqid, r):
    session_info = json.loads(r.get(seqid))
    return session_info
