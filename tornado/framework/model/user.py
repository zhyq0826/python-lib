# -*- coding : utf-8 -*-

from datetime import datetime

from bson.objectid import ObjectId
from pymongo import ASCENDING,DESCENDING
from db.exception import * 
from db.document import Document

class UserDoc(Document):
    collum = {'passwd':0}  
