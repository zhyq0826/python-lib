# -*- coding: UTF-8 -*-
#!/usr/bin/env python


import datetime
import json
import logging
from math import floor

import tornado

from pymongo.collection import Collection
from bson import objectid

from jinja2 import Environment, FileSystemLoader

from code.exceptions import ValidationError

from lib.memsession import MemcacheStore
from lib.session import Session
from lib.queue import Queue

from db import mongo
from config import config

URL_PARAM = {
    '/comment/add': {
        'need': ['comment', 'imgid'],
        'login': True
    },
    '/comment/up': {
        'need': ['id'],
        'login': True
    },
    '/comment/feed': {
        'need': ['skip', 'limit', 'imgid']
    },
}


DEBUG_LIST = []

ENV = Environment(loader=FileSystemLoader(
    config.Path.template), auto_reload=config.DEBUG)


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.db = mongo
        self.queue = Queue()
        self.msg = None
        self._buffer = None
        self.skip = 0
        self.limit = 0

        self.session = Session(self, MemcacheStore(), initializer={
            'nickname': None,
            'uid': None,
            'email': None,
        })
        self.session.processor(self)
        self.env = ENV

    def prepare(self):
        '''
            check current request need or not to be logined
            process query arguments skip and limit
        '''
        path = self.request.path
        argu_keys = self.request.arguments.keys()

        skip = self.get_argument('skip', default=None)
        limit = self.get_argument('limit', default=None)

        self.msg = None
        self._buffer = None

        need_argu = URL_PARAM.get(path, {}).get('need', [])
        need_login = URL_PARAM.get(path, {}).get('login', False)
        if not sorted(list(set(need_argu) & set(argu_keys))) == sorted(need_argu):
            raise tornado.web.HTTPError(404)

        if need_login and not self.session.uid:
            raise tornado.web.HTTPError(404)

        if skip or limit:
            try:
                skip = int(skip)
                limit = int(limit)
                if skip < 0 or limit <= 0:
                    raise
            except Exception as e:
                logging.warning(e)
                raise tornado.web.HTTPError(500)
            else:
                self.skip = skip
                self.limit = limit
        else:
            pass

    def write_error(self, status_code, **kwargs):
        self.render(
            "error.html",
            error_code=status_code,
            msg=''
        )

    # tornado template replaced by jinja2
    def render(self, template_name, **kwargs):
        template = self.env.get_template(template_name)
        html = template.render(**kwargs)
        self.finish(html)


class ServiceHandler(BaseHandler):

    def prepare(self):
        super(BaseHandler, self).prepare()
        pass

    def get(self):
        try:
            self.GET()
        except Exception as e:
            logging.warning(e)
            self._buffer = json.dumps({'code':1, 'msg':'Something is wrong,ops!'})
        else:
            if self._buffer:
                self._buffer = json.dumps(self._buffer)

        jsoncallback = self.get_argument('jsoncallback', default=None)
        if jsoncallback:
            self._buffer = '%s(%s)' % (jsoncallback, self._buffer)

        self.write(self._buffer)

    def post(self):
        try:
            self.POST()
        except Exception as e:
            logging.warning(e)
            self._buffer = json.dumps({'code': 1,'msg':'Something is wrong,ops!'})
        else:
            if self._buffer:
                self._buffer = json.dumps(self._buffer)

        jsoncallback = self.get_argument('jsoncallback', default=None)
        if jsoncallback:
            self._buffer = '%s(%s)' % (jsoncallback, self._buffer)

        self.write(self._buffer)

    def GET(self):
        raise tornado.web.HTTPError(405)

    def POST(self):
        raise tornado.web.HTTPError(405)


class FormHanlder(BaseHandler):

    '''
    @property

    template_name   模板
    >>> template_name = 'index.html'

    row             空的文档对象
    >>> row = {}.fromkeys(['_id','nickname','email','passwd','atime'],None)

    collect         collection
    >>> collect = user

    validation      需要验证的键
    >>> validation = {'required':['email','passwd','nickname'],'validated':['email','nickname','passwd']}

    validators      键对应的validator
    >>> validators = {'email':'validate_email','nickname':'validate_nickname'}

    init_record     初始化新的文档
    >>> init_record = {'atime':datetime.datetime.now(),'number':0}

    required_msg    空消息
    >>> required_msg = {'nickname':'昵称不能为空'}

    error_msg       错误消息
    >>> error_msg = {'nickname':'昵称中含有非法字符'}

    以上所有配置在每个formhandler里进行配置，如果不覆盖，将启用默认配置
    validation-->validated 可以不配置，取默认空，子类覆写 validate 方法来完成所有数据的校验

    default_args    默认重定向的时候url携带的参数，比如父资源的id，pagenum等，以回到当前用户进入的页面,改善用户体验
    >>> default_args = ['cid','pagenum']

    '''
    template_name = ''  # 模板名
    row = {}.fromkeys([], None)  # 空的文档对象
    collect = None  # colletion
    validated_field = {'required':[], 'validated':[]}
    validators = {}
    init_record = {}
    required_msg = {}
    error_msg = {}
    default_args = []

    def __init_request(self):
        self.act = self.get_argument('act', default=None)
        self.callback = {
            'delete': self.delete,
            'create': self.create,
            'edit': self.edit,
            'active': self.active,
            'freeze': self.freeze,
        }

    def prepare(self):
        super(BaseHandler, self).prepare()
        self.__init_request()

    def get(self):
        if self.act:
            self.callback.get(self.act, self._default)()
        else:
            self._home()

    def post(self):
        objid = self.get_argument('id', None)
        if objid:
            self._check_exist()
        self._valide()
        self._post()

    def validate(self):
        pass

    def home():
        pass

    def create(self):
        pass

    def edit(self):
        pass

    def delete(self):
        pass

    def active(self):
        pass

    def freeze(self):
        pass

    #redirect user
    def default(self):
        qs = self._combine_argus(self.request.arguments, self.default_args)
        if qs:
            self.redirect(('%s?%s') % (self.request.path, qs[0:-1]))
        else:
            self.redirect(('%s') % (self.request.path))

    def _combine_argus(self,args,keys=[]):
        qs = ''
        for i in keys:
            if args.get(i, []):
                qs += ('%s=%s&') % (i, args[i][-1])
        return qs

    def _post(self):
        # save document and redirect
        self.collect.save(self.record)
        self.default()

    def _check_exist(self):
        self.record = None
        objid = self.get_argument('id', default=None)
        try:
            if not objid:
                raise
            objid = objectid.ObjectId(objid)

            if self.collect and isinstance(self.collect, Collection):
                self.record = self.collect.find_one({'_id': objid})

            if not self.record:
                raise
        except Exception as e:
            logging.warning(e)
            raise tornado.web.HTTPError(404)

    def _validate(self):
        if not hasattr(self, 'record'):
            self.record = {}
            for k, v in self.init_record.items():
                if isinstance(v, datetime.datetime):
                    self.record[k] = datetime.datetime.now()

                if isinstance(v, list):
                    self.record[k] = [].extend(v)

                if isinstance(v, dict):
                    self.record[k] = {}.update(v)

                if isinstance(v, int):
                    self.record[k] = 0

        try:
            # validate require
            _required_field = self.validated_field.get('required', [])
            for k in _required_field:
                v = self.get_argument(k, default=None)
                self._valide_required(k, v)

                self.record[k] = v

            # validate other
            _validated_field = self.validated_field.get('validated', [])
            for k in _validated_field:
                v = self.get_argument(k, default=None)
                if k in self.validators and hasattr(self, self.validators[k]):
                    getattr(self, self.validators[k])(k, v)

                self.record[k] = v

            # validate other
            self.validate()

        except ValidationError as e:
            self.msg = e

    def _validate_required(self,key,value,msg='empty can not be allowed'):
        if not value:
            msg = self.required_msg.get(key, ('%s %s') % (key, msg))
            raise ValidationError(msg)

    def _validate_number(self,key,value,msg='invalid number'):
        try:
            value = int(value)
        except Exception as e:
            logging.warning(e)
            msg = self.error_msg.get(key, ('%s %s') % (key, msg))
            raise ValidationError(msg)
        else:
            return value

    def _validate_date(self,key,value,msg='invalid date'):
        try:
            value = datetime.datetime.strftime(value, '%Y-%m-%d %H:%M')
        except Exception as e:
            logging.warning(e)
            msg = self.error_msg.get(key, ('%s %s') % (key, msg))
            raise ValidationError(msg)
        else:
            return value


#
# author: zhaoyongqiang
# date:   2012-08-01
# class:  Paginator
# desc:   计算mongodb的分页工具,根据总记录条数
#         和每页大小来计算总共有多少页，以及每页的
#         的skip是多少，可以根据当前页，取得下一页
#         和上一页
#
class Paginator(object):

    """
    paginator tool for mongodb, calculate total pages and  per page skip,
    you can get next page and previous page according to current page

    """
    def __init__(self,total_records=None,per_page=None):

        # total records
        self.total_records = total_records

        # perpage size
        self.per_page = per_page

        # total pages
        self.total_pages = 0

        # perpage skip infor
        self.data = {}

        self.__judge__()

    def __judge__(self):

        # caculate total pages
        if self.total_records > self.per_page:
            self.total_pages = int(floor(
                self.total_records / float(self.per_page)))

            self.data[1] = Page(self, page_number=1, skip=0)

            for i in range(1, self.total_pages):
                self.data[i + 1] = Page(
                    self, page_number=i + 1, skip=self.data[i].skip + self.per_page)

            # 如果计算出来的页数不恰巧是个整数，那么还需要计算最后一页
            if self.total_pages < (self.total_records / float(self.per_page)):
                # 计算最后一页,因为最后一页肯定是能全页显示的
                self.data[self.total_pages + 1] = Page(self, self.total_pages + 1, skip=self.data[self.total_pages].skip + self.per_page)
                # 页数added 1
                self.total_pages = self.total_pages + 1
        else:
            self.total_pages = 1
            self.data[1] = Page(self, 1, skip=0)

    def get_page(self, page_number):
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

        self.page_number = page_number

        self.skip = skip

        self.paginator = paginator

        self.next_page_number = self.page_number + 1

        self.prev_page_number = self.page_number - 1

    def has_next(self):
        return self.page_number < self.paginator.total_records / float(self.paginator.per_page)

    def has_prev(self):
        return self.page_number > 1

    def get_next_page(self):
        return self.paginator.get_page(self.next_page_number)

    def get_prev_page(self):
        return self.paginator.get_page(self.prev_page_number)


#
# author: zhaoyongqiang
# date:   2012-08-01
# def:    cal_start_end_by_today
# desc:   根据前端页面参数计算起始和结束日期，并且
#         返回起始和终止日期
#

def cal_start_end_by_today(date_argument):

    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day

    start = None
    end = None

    if not date_argument:
        return start, end

    last_days_dic = {'lastday': 1,'lastthree':3,'lastweek':7,'lastmonth':30,'lastthreemonth':90}
    if date_argument == 'today':
        tomorrow = today + datetime.timedelta(1)
        end = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        start = datetime.datetime(year, month, day)
    elif date_argument in last_days_dic.keys():
        last_days = today - datetime.timedelta(last_days_dic[date_argument])
        start = datetime.datetime(
            last_days.year, last_days.month, last_days.day)
        end = datetime.datetime(year, month, day)

    return start, end


#
# author: zhaoyongqiang
# date:   2012-09-10
# def:    transfer_pagenum_offset
# desc:   转换pagenum和offset
#
def transfer_pagenum_offset(pagenum, limit):
    try:
        pagenum = abs(int(pagenum))
        if pagenum == 0:
            raise
        offset = (pagenum - 1) * limit
    except Exception as e:
        logging.warning(e)
        pagenum = 1
        offset = 0

    return pagenum, offset
