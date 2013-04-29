#-*- coding: utf-8 -*-
import logging

import gridfs
from pymongo import Connection

import dbconf

try:
    conn = Connection(host=dbconf.master)
except Exception as e:
    logging.warning(e)
    raise e

db = conn['db']
db_file = gridfs.GridFS(conn['db_file'])

"""
  user              用户表
  ----------------- ------------------------------
  email:            注册邮箱
  nickname:         昵称
  passwd:           密码，明文
  avatar:           头像
  gender:           性别
  lastlogin:        最后一次登录
  atime:            注册时间
"""
user = db['user']
user.count()
