import tornado.ioloop
import tornado.web as web
import tornadio2

class MyConnection(tornadio2.SocketConnection):

    @classmethod
    def init(cls):
        cls.clients = set()
        cls.master = None
        cls.slide = None

    def on_open(self, request):
        host = request.get_argument("host")
        if host and host == "ron":
            MyConnection.master = self
        else:
            MyConnection.clients.add(self)
            self._send_current_slide()

    @tornadio2.event("like")
    def on_like(self, slide_number):
        if MyConnection.master is not None:
            MyConnection.master.emit("like", slide_number)

    @tornadio2.event("slide_transfer")
    def on_slide_transfer(self, slide_header, slide_number):
        if self is not MyConnection.master:
            return

        MyConnection.slide = {"slide_header" : slide_header, "slide_number" : slide_number}

        self._update_clients()

    def _update_clients(self):
        for c in MyConnection.clients:
            c._send_current_slide()

    def _send_current_slide(self):
        print "sending ", MyConnection.slide
        self.emit("slide", MyConnection.slide)

    def on_close(self):
        if self is MyConnection.master:
            MyConnection.slide = None
            MyConnection.master = None
            self._update_clients()
        else:
            MyConnection.clients.remove(self)

MyRouter = tornadio2.TornadioRouter(MyConnection)
MyConnection.init()

routes = [
    (r"/static/(.*)", web.StaticFileHandler, {"path": "./static"}),
    (r"/html/(.*)", web.StaticFileHandler, {"path": "./"})]
routes.extend(MyRouter.urls)

application = web.Application(routes, socket_io_port = 8000)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
