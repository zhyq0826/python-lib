#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import urllib2
import urllib
import json
import logging
import time
import datetime
from bson import objectid
from xml.dom import minidom 

sys.path += [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]

from db import business_mongo 

DEBUG = True

cid = 'bip1065_10491_001'

HOST = 'http://ad2.easou.com:8080/j10ad/hot3.jsp?cid='+cid+'&size='

def gettext(node):
    if node and node.nodeType == node.TEXT_NODE:
        return node.nodeValue
    return None

def syceso(n):
    logger=logging.getLogger()
    if DEBUG:
        handler=logging.FileHandler("eso.log")
    else:    
        handler=logging.FileHandler("/var/log/eso.log")

    logger.addHandler(handler)
    logger.setLevel(logging.NOTSET)

    request_url = '%s%s'%(HOST,n)
    response = None
    
    as_list = []
    counter = 2
    while True:
        try:
            response = urllib2.urlopen(request_url,timeout=10000)
            if response.code != 200:
                raise
            dom = minidom.parseString(response.read().strip())
            now = str(datetime.datetime.now())
            count = 0
            items = dom.getElementsByTagName('item')
            for i in items:
                if count%100 ==0:
                    time.sleep(1)

                word_node = i.firstChild.firstChild
                url_node = i.lastChild.firstChild
                word = gettext(word_node)
                url = gettext(url_node)
                if word and url:
                    as_list.append((word,url))
                count +=1            

            s = ('%s\t\t%s synchronous success')%(request_url,now)
            logger.info(s)
        except Exception as e:
            s = ('%s\t\t%s synchronous failed')%(request_url,now)
            logger.info(s)
            logger.warning(e)
            as_list = []
            counter -= 1
            if counter<0:
                break
            else:
                continue
        else:
            break
    
    if len(as_list) > 0:
      business_mongo.easou_keyword.remove()
      for i in as_list:
          business_mongo.easou_keyword.insert({'key':i[0],'url':i[1],'atime':datetime.datetime.now()})


if __name__ == '__main__':
    try:
        size = int(sys.argv[-1])
    except:
        size = 1000
    syceso(size)
