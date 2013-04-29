#-*- coding:utf-8 -*-

import unittest
import os
import sys
from datetime import datetime

from bson.objectid import ObjectId


root_path = [os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)]
sys.path += root_path

from model import db_user


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # guarantee document key is consistency
    def test_document_create(self):
        user = {'nickname': 'hello','email':'zhyq0826@126.com','passwd':''}
        self.assertTrue(isinstance(db_user.create(user), ObjectId))

    # guarantee all data is str
    def test_document_to_str(self):
        s = db_user.to_str(db_user.find_one())
        for k, v in s.items():
            self.assertTrue(not isinstance(v, ObjectId) and not isinstance(v, datetime))

if __name__ == '__main__':
    unittest.main()
