# -*- coding:utf-8 -*-

"""
File Name : 'pretty_log'.py
Description:
Author: 'btows'
Date: '18-1-6' '下午4:01'
"""

import pprint


def pretty_print(content):
    o = pprint.pformat(content)
    return str(o)
