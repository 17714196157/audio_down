# -*- coding:utf-8 -*-

"""
File Name : 'redis_op'.py
Description:
Author: 'btows'
Date: '18-1-8' '下午7:24'
"""
import json


# key有效期1天，86400秒
def redis_expire(seqid, r):
    r.expire(seqid, 86400)


# redis状态更新
def redis_record(seqid, port, cfg_name, wav_file, status, sentence, r):
    try:
        value = {"port": port, "cfg_name": cfg_name, "wav_file": wav_file, "status": status, 'sentence':sentence}
        redis_value = json.dumps(value)
        r.set(seqid, redis_value)
        redis_expire(seqid, r)
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