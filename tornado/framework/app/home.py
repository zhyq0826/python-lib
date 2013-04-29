from base import BaseHandler,ServiceHandler,FormHandler
from db import mongo


class Home(BaseHandler):

    def get(self):
        as_dict = [
            {'_id': 1,'k':'sd','v':'sad'},
            {'_id': 2,'k':'d','v':'sad'}
        ]
        self.render('test.html',as_dict=as_dict)


class TestServiceHandler(ServiceHandler):

    def GET(self):
