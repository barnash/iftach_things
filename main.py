import tornado.ioloop
import tornado.web as web
import tornadio2

class MyConnection(tornadio2.SocketConnection):
    def on_open(self, *args, **kwargs):
        print "open"
        self.emit("slide", {"slide_number": 2, "slide_header" : "My first cool slide"})

    @tornadio2.event("like")
    def on_like(self):
        print "liked it!"

    def on_close(self):
        print "closed"

MyRouter = tornadio2.TornadioRouter(MyConnection)

routes = [
    (r"/static/(.*)", web.StaticFileHandler, {"path": "./static"}),
    (r"/html/(.*)", web.StaticFileHandler, {"path": "./"})]
routes.extend(MyRouter.urls)

application = web.Application(routes, socket_io_port = 8000)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
