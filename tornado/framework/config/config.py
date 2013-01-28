#coding: utf-8
import logging
import os,sys

#debug flag
DEBUG = True 

#tornado process gzip
GZIP = True

#redis db
QUEUE_DB = 0
CACHE_DB = 1

#logging
if DEBUG:
    LOG_FILENAME = 'server.log'
    LOG_LEVEL = logging.DEBUG 
    LOG_PATH = ''
    print 'the server is starting'
    print 'log mode is debug ...'
    print 'log file is in current directory called '+LOG_FILENAME+'. Good work!\n'
else:
    LOG_FILENAME = 'server.log'
    LOG_LEVEL = logging.ERROR
    LOG_PATH = '/var/log/'


class Path:
    root_path = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
                )
            )
    template = os.path.join(root_path,'template')
    tool_path = os.path.join(root_path,"tools")
    axmlprinter2 = os.path.join(tool_path, "AXMLPrinter2.jar")

class Memcache:
    server = ['127.0.0.1:11211']
    timeout = 3600*24*3

class Queue:
    host = "localhost"
    port = 6379
    db = QUEUE_DB
    mail_queue = 'send_mail'
    queue = [mail_queue]

class Cache:
    master = "localhost" 
    slaves = ['localhost']
    port = 6379
    db = CACHE_DB

