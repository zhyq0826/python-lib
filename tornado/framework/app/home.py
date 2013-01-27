from base import BaseHandler

class Home(BaseHandler):

    def get(self):
        self.write('')
