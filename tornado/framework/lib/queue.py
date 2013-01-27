#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import redis
import os,sys

from config import config
from db import mongo
from encoder import MongoEncoder

class Queue:

    def __init__(self):
        self.r = redis.Redis(config.Queue.host, config.Queue.port, config.Queue.db)

    def add(self, name, data):
        score = time.time()
        self.r.zadd(name, data, score)

    def pop(self, name):
        min_score = 0
        max_score = time.time()

        result = self.r.zrangebyscore(
                name, min_score, max_score, start=0, num=1, withscores=False)
        if not result:
            return False

        if len(result) == 1:
            data = result[0]
            self.r.zrem(name, result[0])
            return data
        else:
            return False


