#!/usr/bin/env python
#-*-coding:utf-8-*-

import traceback
from pymongo import DESCENDING, ASCENDING
from redis import Redis
from bson import objectid
import os, sys, json, time, threading

sys.path += [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]

from conf import config
from lib import utils, queue, oset
from lib.encoder import MongoEncoder

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

lock = threading.Lock()

"""
handlers
"""
def send_mail(task, num):
    task = json.loads(task)
    email = task['email']
    code = task['code']
    t = task['t']
    name = unicode(task['name'])
    print 'Slave [ %d ] send email to %s' % (num, task['email'])
    if t == 0:
        utils.sendmail(config.Mail._from,
                email,
                config.Mail._hello_subject,
                config.Mail._hello_message % (name,str(code))
                )
    else:
        utils.sendmail(config.Mail._from,
                email,
                config.Mail._reset_subject,
                config.Mail._reset_message % (name,str(code))
                )

class SlaveAlpha(threading.Thread):
    def __init__(self, num):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.num = num

        print 'Slave [ %d ] start' % num

        while True:
            time.sleep(0.5)
            try:
                for i in config.Queue.queue:
                    try:
                        with lock: task = self.queue.pop(i)
                    except:
                        self.queue.remove(i)

                    if not task:
                        continue

                    exec('%s(task, self.num)' % i)
            except:
                print 'Slave [ %d ] error occur: %s' % (self.num, traceback.format_exc())


def main():
    slaves = []

    for i in range(8):
        s = SlaveAlpha(i)
        slaves.append(s)
        s.start()

    for i in slaves:
        i.join()

if __name__ == '__main__':
    main()
