# -*- coding: UTF-8 -*-
#!/usr/bin/env python


import os,sys
from math import ceil,floor
import datetime
from struct import pack,unpack
from hashlib import sha256

import tornado

from pymongo.collection import Collection
from bson import objectid

from jinja2 import Environment,FileSystemLoader 

from lib.memsession import MemcacheStore
from lib.session import Session
from lib.queue import Queue

from db import mongo
from config import config

URL_PARAM ={
    '/comment/add':{
        'need':['comment','imgid'],
        'login':True
        },
    '/comment/up':{
        'need':['id'],
        'login':True
        },
    '/comment/feed':{
        'need':['skip','limit','imgid']
        },
}


DEBUG_LIST = []

#todo check webpy session
def debug_process():
    print 'current unreleased object is about ',len(as_list)
    print 'these object are below: address --> refference count'
    for i in as_list:
        print id(i),'-->',sys.getrefcount(i)

ENV = Environment(loader=FileSystemLoader(config.Path.template),auto_reload=config.DEBUG)

class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.db = mongo
        self.queue = Queue()
        self.msg = None
        self._buffer = None
        self.skip = 0 
        self.limit = 0 

        self.session = Session(self,MemcacheStore(),
                    initializer = {
                        'nickname': None,
                        'uid': None,
                        'email': None,
                        }
                    )
        self.session.processor(self)
        self.env = ENV
        
        if config.DEBUG:
            if self.session._data not in DEBUG_LIST:
                DEBUG_LIST.append(self.session._data)
                debug_process()

    def prepare(self):
        '''
            check current request need or not to be logined
            process query arguments skip and limit
        '''
        path = self.request.path
        argu_keys = self.request.arguments.keys()

        skip = self.get_argument('skip',default=None)
        limit = self.get_argument('limit',default=None)

        self.msg = None
        self._buffer = None
        
        need_argu = URL_PARAM.get(path,{}).get('need',[])
        need_login = URL_PARAM.get(path,{}).get('login',False)        
        if not sorted(list(set(need_argu) & set(argu_keys)))==sorted(need):
            raise tornado.web.HTTPError(404)
        
        if need_login and not self.session.uid:
            raise tornado.web.HTTPError(404)
        
        if skip or limit:
            try:
                skip = int(skip)
                limit = int(limit)
                if skip <0 or limit <=0:
                    raise
            except Exception ,e:
                raise tornado.web.HTTPError(500)
            else:
                self.skip = skip
                self.limit = limit
        else:
            pass
    
    def write_error(self,status_code, **kwargs):
        self.render(
                "error.html",
                error_code=status_code,
                msg = ''
                )

    #tornado template replaced by jinja2 
    def render(self,template_name,**kwargs):
        template = self.env.get_template(template_name)
        html = template.render(**kwargs)
        self.finish(html)


class ServiceHandler(BaseHandler):


    def prepare(self):
        super(BaseHandler,self).prepare()
        pass

    def get(self):    
        try:
            self.GET()
        except Exception,e :
            logging.warning(e)
            self._buffer = json.dumps({'code':1,'msg':'error'})
        else:
            if self._buffer:
                self._buffer = json.dumps(self._buffer)
                
        jsoncallback = self.get_argument('jsoncallback',default=None)
        if jsoncallback:
            self._buffer = '%s(%s)' % (jsoncallback,self._buffer)

        self.write(self._buffer)
            
    def post(self):
        try:
            self.POST()
        except Exception ,e:
            logging.warning(e)
            self._buffer = json.dumps({'code':1,'msg':'error'})
        else:
            if self._buffer:
                self._buffer = json.dumps(self._buffer)
                
        jsoncallback = self.get_argument('jsoncallback',default=None)
        if jsoncallback:
            self._buffer = '%s(%s)' % (jsoncallback,self._buffer)

        self.write(self._buffer)


    def GET(self):
        raise tornado.web.HTTPError(405)
    
    def POST(self):
        raise tornado.web.HTTPError(405)


class FormHanlder(BaseHandler):

    template_name = '' 
    row = {}.fromkeys([],None)
    collect = None
    validation = {'required':[]}
    init_record = {'atime':datetime.datetime.now()}
    required_msg = {}
    error_msg = {}

    def __init_request(self):
        self.act = self.get_argument('act',default=None)
        self.callback = {
                'delete':self._delete,
                'create':self._create,
                'edit':self._edit,
                'active':self._active,
                'freeze':self._freeze,
                }

    def prepare(self):
        super(BaseHandler,self).prepare()
        self.__init_request()

    def get(self):
        if self.act:
            self.callback.get(self.act,self._default)()
        else:
            self._home()

    def post(self):
        objid = self.get_argument('id',None)
        if objid:
            self._check_exist()
        self._valide()
        self._post()

    def _post(self):
        pass

    def _home():
        pass

    def _create(self):
        pass

    def _edit(self):
        pass

    def _delete(self):
        pass

    def _active(self):
        pass

    def _freeze(self):
        pass

    def _check_exist(self):
        self.record = None
        objid = self.get_argument('id',default=None)
        try:
            if not objid:
                raise
            objid = objectid.ObjectId(objid)

            if self.collect and isinstance(self.collect,Collection):
                self.record = self.collect.find_one({'_id':objid})
            
            if not self.record:
                raise
        except Exception, e:
            raise tornado.web.HTTPError(404)

    def _valide():
        if not hasattr(self,'record'):
            self.record = {}
            for k,v in self.init_record.items():
                if isinstance(v,datetime.datetime):
                    self.record[k] = datetime.datetime.now()

                if isinstance(v,list):
                    self.record[k] = [].extend(v)

                if isinstance(v,dict):
                    self.record[k] = {}.update(v)

                if isinstance(v,int):
                    self.record[k] = 0

        try:
            _required = self.validation.get('required',[])
            for k in _required:
                v = self.get_argument(k,default=None)
                self._valide_required(k,v)

            for k in self.validation.get('valide',{}):
                pass
                #todo 
        except Exception, e:
            raise e

    def _valide_required(self,key,value,msg='field can not be empty'):
        if not value:
            self.msg = self.required_msg.get(k,('%s-%s')%(k,msg))
            raise

    def _valide_number(self,key,value,msg='field can not be number'):
        try:
            value = int(value)
            self.msg = self.error_msg.get(k,('%s-%s')%(k,msg))
        except Exception, e:
            raise
        else:
            return value


##################################################
# author: zhaoyongqiang 
# date:   2012-08-01
# class:  Paginator
# desc:   计算mongodb的分页工具,根据总记录条数
#         和每页大小来计算总共有多少页，以及每页的
#         的skip是多少，可以根据当前页，取得下一页
#         和上一页
##################################################
class Paginator(object):
    """
    paginator tool for mongodb, calculate total pages and  per page skip,
    you can get next page and previous page according to current page

    """
    def __init__(self,total_records=None,per_page=None):

        #total records
        self.total_records = total_records
        
        #perpage size
        self.per_page = per_page
        
        #total pages
        self.total_pages = 0

        #perpage skip infor
        self.data={}

        self.__judge__()


    def __judge__(self):
        
        #caculate total pages 
        if self.total_records>self.per_page:
            self.total_pages = int(floor(self.total_records/float(self.per_page)))

            self.data[1]=Page(self,page_number=1,skip=0)

            for i in range(1,self.total_pages):
                self.data[i+1]=Page(self,page_number=i+1,skip=self.data[i].skip+self.per_page)

            #如果计算出来的页数不恰巧是个整数，那么还需要计算最后一页
            if self.total_pages<(self.total_records/float(self.per_page)):
                #计算最后一页,因为最后一页肯定是能全页显示的
                self.data[self.total_pages+1]=Page(self,self.total_pages+1,skip=self.data[self.total_pages].skip+self.per_page)
                #页数added 1
                self.total_pages = self.total_pages+1
        else:
            self.total_pages=1
            self.data[1]=Page(self,1,skip=0)

    def get_page(self,page_number):
        page_number = int(page_number)
        if page_number in self.data.keys():
            return self.data[page_number]
        else:
            return None



class Page(object):
    """
    page include per page skip infor and it's previous page
    and next page infor if they both exits
    """
    def __init__(self,paginator,page_number=1,skip=0):

        self.page_number=page_number

        self.skip = skip

        self.paginator = paginator

        self.next_page_number = self.page_number+1

        self.prev_page_number = self.page_number-1

    def has_next(self):
        return self.page_number<self.paginator.total_records/float(self.paginator.per_page)

    def has_prev(self):
        return self.page_number>1

    def get_next_page(self):
        return self.paginator.get_page(self.next_page_number)

    def get_prev_page(self):
        return self.paginator.get_page(self.prev_page_number)


##################################################
# author: zhaoyongqiang 
# date:   2012-08-01
# def:    cal_start_end_by_today 
# desc:   根据前端页面参数计算起始和结束日期，并且
#         返回起始和终止日期
##################################################

def cal_start_end_by_today(date_argument):

    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day

    start = None
    end = None
    
    if not date_argument:
        return start,end

    last_days_dic={'lastday':1,'lastthree':3,'lastweek':7,'lastmonth':30,'lastthreemonth':90}
    if date_argument =='today':
        tomorrow=today+datetime.timedelta(1)
        end = datetime.datetime(tomorrow.year,tomorrow.month,tomorrow.day)
        start = datetime.datetime(year,month,day)
    elif date_argument in last_days_dic.keys():
        last_days = today-datetime.timedelta(last_days_dic[date_argument])
        start = datetime.datetime(last_days.year,last_days.month,last_days.day)
        end = datetime.datetime(year,month,day)

    return start,end


##################################################
# author: zhaoyongqiang 
# date:   2012-09-10
# def:    transfer_pagenum_offset 
# desc:   转换pagenum和offset
##################################################
def transfer_pagenum_offset(pagenum,limit):
    try:
        pagenum = abs(int(pagenum))
        if pagenum==0:
            raise
        offset = (pagenum-1)*limit
    except Exception, e:
        pagenum=1
        offset=0

    return pagenum,offset

