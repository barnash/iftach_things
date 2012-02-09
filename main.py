import tornado.ioloop
import tornado.web as web
import tornadio2

class MyConnection(tornadio2.SocketConnection):
    clients = set()
    master = None
    slide = None

    def on_open(self, info):
        self.clients.add(self)
        self._send_current_slide()

    @tornadio2.event("like")
    def on_like(self, slide):
        if self.master is not None:
            self.master.emit("like", slide)

    @tornadio2.event("slide_transfer")
    def on_slide_transfer(self):
        if self is not self.master:
            return

        self.slide = {"slide_number": 2, "slide_header" : "My first cool slide"}

        self._update_clients()

    def _update_clients(self):
        for c in self.clients:
            c._send_current_slide()

    def _send_current_slide(self):
        self.emit("slide", self.slide)

    def on_close(self):
        if self is self.master:
            self.slide = None
            self.master = None
            self._update_clients()
        else:
            self.clients.remove(self)

MyRouter = tornadio2.TornadioRouter(MyConnection)

routes = [
    (r"/static/(.*)", web.StaticFileHandler, {"path": "./static"}),
    (r"/html/(.*)", web.StaticFileHandler, {"path": "./"})]
routes.extend(MyRouter.urls)

application = web.Application(routes, socket_io_port = 8000)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
