#!/usr/bin/python
#-*- encode: UTF-8 -*-

import os
import re
import logging
import sys

import tornado.web
import tornado.httpserver
import tornado.options
from tornado.options import define, options

from config import config
from app import home

define("port", default=8888, type=int)

class ErrorHandler(tornado.web.RequestHandler):

    def initialize(self,status_code):
        self.set_status(status_code)

    def prepare(self):
        self.render('error.html',error_code = self._status_code)


class Application(tornado.web.Application):
    def __init__(self):
        handlers =[
                (r'/',home.Home),
                ]

        settings = dict(
                template_path = os.path.join(os.path.dirname(__file__),"template"),
                static_path = os.path.join(os.path.dirname(__file__),"static"),
                xsrf_cookies = False,
                cookie_secret = "aVD321fQAGaYdkLlsd334K#/adf22iNvdfdflle3fl$=",
                login_url = "/login",
                autoescape = None,
                debug = config.DEBUG,
                gzip = config.GZIP,
                )

        tornado.web.Application.__init__(self, handlers, **settings)
        tornado.web.ErrorHandler = ErrorHandler


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

def initlog(console=False):
    if console:
        fh = logging.StreamHandler()
    else:
        fh = logging.handlers.RotatingFileHandler('%s%s' % (config.LOG_PATH,config.LOG_FILENAME),
                maxBytes=500*1024*1024,
                backupCount=3)
        formatter = logging.Formatter('%(levelname)-8s %(asctime)s %(module)s:%(lineno)d:%(funcName)s %(message)s')
        fh.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(fh)
    root_logger.setLevel(config.LOG_LEVEL)

if __name__ == '__main__':
    try:
        console = sys.argv[-1]
        if console != '1':
            console =0
    except:
        console = 0 

    initlog(console)
    main()
