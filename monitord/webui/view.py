from tornado import web


class RootHandler(web.RequestHandler):

    def get(self):
        self.render('templates/index.html')
