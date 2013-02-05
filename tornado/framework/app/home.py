from base import BaseHandler

class Home(BaseHandler):

    def get(self):
        as_dict = [
                {'_id':1,'k':'sd','v':'sad'},
                {'_id':2,'k':'d','v':'sad'}
                ]
        self.render('test.html',as_dict=as_dict)
