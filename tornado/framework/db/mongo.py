#coding: utf-8
# -*- coding: utf-8 -*-

import gridfs
from pymongo import Connection
from pymongo.master_slave_connection import MasterSlaveConnection

import dbconf

try:
    dbconf.slave
except:
    conn = Connection(host=dbconf.master)
else:
    master_conn = Connection(host=dbconf.master)
    slave_conns = [Connection(host=i) for i in dbconf.slave]
    conn = MasterSlaveConnection(master_conn, slave_conns)

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

