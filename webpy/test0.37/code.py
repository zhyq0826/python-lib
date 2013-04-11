import web
import os

render = web.template.render('templates/')

root_path = os.path.dirname(os.path.abspath(__file__)) 
image_path = os.path.join(root_path,'static/image/')

class index:

    def GET(self):
        i = web.input(name=None)
        #print i
        if i.name and not web.ctx.session.name:
            web.ctx.session.name = i.name


        print 'handler session ', id(web.ctx.session)
        print 'handler session id ',web.ctx.session.session_id
        print 'handler session name',web.ctx.session.name
        referer = web.ctx.env.get('HTTP_REFERER','http://google.com')
        #print referer
        #print web.ctx
        #print type(web.ctx)
        #print web.ctx.keys()
        #for k,v in web.ctx.items():
            #print k,' ',v
        #for j in web.ctx:
            #print j
            # if isinstance(web.ctx[j],dict):
            #     for k,v in web.ctx[j].items():
            #         pass
            #         #print k,v
            # else:
            #     pass
                #print j,web.ctx[j]

        return render.hello(name=i.name,sid=web.ctx.session.session_id)

class rxml:

    def GET(self,code):
        web.header('Content-Type','text/xml')
        return render.txml(code)
        #return web.notfound(render.notfound())
        #return web.notfound(str(render.notfound()))

class not404:

    def GET(self):
        raise web.notfound('sorry not found')

import time
class download:

    def GET(self):
        web.header('Content-Type','image/jpeg') 
        web.header('Transfer-Encoding','chunked')
        f = open(os.path.join(image_path,'mz.jpg'))
        while True:
            data = f.read(1024)
            time.sleep(2)
            if not data:
                break
            yield data
        

def internalerror():
    return web.internalerror('Bad server')

def notfound():
    return web.notfound('sorry the page you are looking for was not found')

def my_loadhook():
    print 'my load hook'

def my_unloadhook():
    print 'my unload hook'

urls = (
        '/','index',
        '/xml/(.*)','rxml',
        '/404',not404,
        '/download','download'
    )

app = web.application(urls,globals())
session = web.session.Session(app,web.session.DiskStore('sessions'),initializer={'count':0,'name':None})

def session_hook():
    web.ctx.session = session

#application processors to do something before request after request
print 'app session ',id(session)

app.add_processor(web.loadhook(session_hook))
#app.add_processor(web.loadhook(my_loadhook))
#app.add_processor(web.unloadhook(my_unloadhook))

app.internalerror = internalerror
#app.notfound = notfound

if __name__ == '__main__':
    app.run()
