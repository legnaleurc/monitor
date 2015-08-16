import urllib.parse as up
import json

from tornado import web, ioloop, auth, httpclient, gen, httputil

from monitord import db, util


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


class GithubOauth2Mixin(auth.OAuth2Mixin):

    _OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    _OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'

    @gen.coroutine
    def get_authenticated_user(self, client_id, client_secret, code, redirect_uri):
        body = up.urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
        })
        client = self.get_auth_http_client()
        response = yield client.fetch(self._OAUTH_ACCESS_TOKEN_URL, method='POST', headers={
            'Accept': 'application/json',
        }, body=body)
        data = json.loads(response.body.decode('utf-8'))
        return data

    def get_auth_http_client(self):
        return httpclient.AsyncHTTPClient()


class LoginHandler(web.RequestHandler, GithubOauth2Mixin):

    @gen.coroutine
    def get(self):
        gh = settings.GITHUB
        redirect_uri = gh['redirect_uri']
        client_id = gh['client_id']
        client_secret = gh['client_secret']

        state = self.get_argument('state', None)

        if not state:
            # user triggered
            self.authorize_redirect(redirect_uri=redirect_uri, client_id=client_id, scope=['read:org'], extra_params={
                'state': 'acquire_code',
            })
        elif state == 'acquire_code':
            code = self.get_argument('code', None)
            if not code:
                self._handler_error()
                return

            # get access token
            info = yield self.get_authenticated_user(client_id=client_id, client_secret=client_secret, code=code, redirect_uri=redirect_uri)
            github_token = info['access_token']

            info = yield self._update_database(github_token)

            self.write({
                'info': info,
            })
        else:
            raise web.HTTPError(404)

    @gen.coroutine
    def _update_database(self, github_token):
        gh_client = util.GithubClient(github_token)
        # get user info
        code, user = yield gh_client.get_user()
        if code != 200:
            raise web.HTTPError(404)
        name = user['login']

        # get team info
        code, teams = yield gh_client.get_teams()
        if code != 200:
            raise web.HTTPError(404)
        teams = filter(lambda __: __['organization']['login'] == 'adsbypasser', teams)
        teams = {__['permission'] for __ in teams}
        if 'admin' in teams:
            admin, write, read = True, True, True
        elif 'pull' in teams:
            admin, write, read = False, True, True
        else:
            admin, write, read = False, False, True

        # update user information
        with db.scoped() as session:
            user = session.query(db.User).filter(db.User.name == name).first()
            if user:
                user.github_token = github_token
                user.admin = admin
                user.write = write
                user.read = read
            else:
                user = db.User(name=name, github_token=github_token, admin=admin, write=write, read=read)
                session.add(user)

        return admin, write, read

    def _handler_error(self):
        logger = util.get_logger()

        error = self.get_argument('error')
        error_uri = self.get_argument('error_uri')
        error_description = self.get_argument('error_description')

        logger.error(error)
        logger.error(error_uri)
        logger.error(error_description)
