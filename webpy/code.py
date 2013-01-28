import web
import os
render = web.template.render('templates/')

root_path = os.path.dirname(os.path.abspath(__file__)) 
image_path = os.path.join(root_path,'/static/image/')

class index:

    def GET(self):
        i = web.input(name=None)
        print i
        referer = web.ctx.env.get('HTTP_REFERER','http://google.com')
        print referer
        for j in web.ctx:
            if isinstance(web.ctx[j],dict):
                for k,v in web.ctx[j].items():
                    print k,v
            else:
                print j,web.ctx[j]

        return render.hello(name=i.name)

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
        f = open('static/image/mz.jpg')
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

#application processors to do something before request after request
app = web.application(urls,globals())

app.add_processor(web.loadhook(my_loadhook))
app.add_processor(web.unloadhook(my_unloadhook))

app.internalerror = internalerror
#app.notfound = notfound

if __name__ == '__main__':
    app.run()


