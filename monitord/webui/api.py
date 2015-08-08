from tornado import web, ioloop


class RunHandler(web.RequestHandler):

    def get(self):
        ctlr = self.application.settings['controller']
        loop = ioloop.IOLoop.current()

        loop.add_callback(ctlr.queue_test)


class CancelHandler(web.RequestHandler):

    def get(self):
        ctlr = self.application.settings['controller']
        loop = ioloop.IOLoop.current()

        loop.add_callback(ctlr.cancel_test)
