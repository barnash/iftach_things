import tornado.ioloop
import tornado.web as web
import tornadio2

class MyConnection(tornadio2.SocketConnection):

    @classmethod
    def init(cls):
        cls.clients = set()
        cls.master = None
        cls.old_master_connections = set()
        cls.slide = None
        cls.likes = {}

    def on_open(self, request):
        host = request.get_argument("host")
        if host and host == "ron":
            if MyConnection.master is not None:
                MyConnection.old_master_connections.add(MyConnection.master)
            MyConnection.master = self
            MyConnection.slide = None
            self._update_clients()
        else:
            MyConnection.clients.add(self)
            self._send_current_slide()

    @tornadio2.event("like")
    def on_like(self, slide_number):
        if self._add_like(slide_number):
            if MyConnection.master is not None:
                MyConnection.master.emit("like", slide_number)

    @tornadio2.event("slide_transfer")
    def on_slide_transfer(self, slide_header, slide_number):
        if self is not MyConnection.master:
            return

        MyConnection.slide = {"slide_header" : slide_header, "slide_number" : slide_number}

        self._update_clients()

    @tornadio2.event("get_likes")
    def get_likes(self, slide_number):
        if slide_number not in MyConnection.likes.keys():
            return 0
        r = len(MyConnection.likes[slide_number])
        return r

    def _update_clients(self):
        for c in MyConnection.clients:
            c._send_current_slide()

    def _send_current_slide(self):
        self.emit("slide", MyConnection.slide)

    def _add_like(self, slide_number):
        if slide_number not in MyConnection.likes.keys():
            MyConnection.likes[slide_number] = set()
        if self in MyConnection.likes[slide_number]:
            return False
        MyConnection.likes[slide_number].add(self)
        return True

    def on_close(self):
        if self is MyConnection.master:
            print "master removed - no master"
            MyConnection.slide = None
            MyConnection.master = None
            self._update_clients()
        elif self in MyConnection.old_master_connections:
            print "old master removed"
            MyConnection.old_master_connections.remove(self)
        elif self in MyConnection.clients:
            print "client removed"
            MyConnection.clients.remove(self)
        else:
            raise Error("Bug! this connection is unknown - this must be a bug")

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
