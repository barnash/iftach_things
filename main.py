import tornado.ioloop
import tornado.web as web
import tornadio2

class MainHandler(web.RequestHandler):
	def get(self):
		self.write("Hello, world")

class MyConnection(tornadio2.SocketConnection):

	def on_open(self, *args, **kwargs):
		print "open"

	def on_message(self, message):
		print "hi"

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
