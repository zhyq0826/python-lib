#!/usr/bin/python
#-*-encoding:utf-8-*-
import time
import datetime
import os
import sys
import  StringIO
import Image
from pymongo import DESCENDING, ASCENDING
from bson import objectid

reload(sys)
sys.setdefaultencoding('utf-8')

root_path = [os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
            )
       )]
sys.path += root_path

from db import mongo

def get_image_by_objid(objid):
    try:
        img = Image.open(StringIO.StringIO(mongo.imgfs.get(objid).read()))
    except:
        return None
    else:
        return img 

def crop_image(img,box):
    try:
        crop_img = img.crop(box)
    except:
        return None
    else:
        return crop_img

def save_image(img,file_type="JPEG"):
    output = StringIO.StringIO()
    try:
        img.save(output,file_type,quality=90)
    except:
        img.convert("RGB")
        img.save(output,file_type,quality=90)
        
    objid = mongo.imgfs.put(output.getvalue())
    output.close()
    return objid

def resize_image(img,scale):
    try:
        resize_img = img.resize(scale)
    except:
        return None
    else:
        return resize_img


