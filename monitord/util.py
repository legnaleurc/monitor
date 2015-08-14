import logging
import tempfile
import os.path as op
import urllib.parse as up
import json

from tornado import log, gen, httpclient, httputil


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def setup_logger():
    log.enable_pretty_logging()

    logger = get_logger()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(op.join(tempfile.gettempdir(), 'monitord.log'))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('{asctime}|{levelname:_<8}|{message}', style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger():
    return logging.getLogger('monitord')


@gen.coroutine
def http_get(url, query=None, headers=None):
    if query is None:
        query = {}
    client = httpclient.AsyncHTTPClient()
    url = httputil.url_concat(url, query)
    request = httpclient.HTTPRequest(url, method='GET', headers=headers)
    response = yield client.fetch(request, raise_error=False)
    return response.code, response.body


@gen.coroutine
def http_post(url, query=None, headers=None):
    if query is None:
        query = {}
    client = httpclient.AsyncHTTPClient()
    query = up.urlencode(query)
    request = httpclient.HTTPRequest(url, method='POST', headers=headers, body=query)
    response = yield client.fetch(request, raise_error=False)
    return response.code, response.body


class GithubClient(object):

    def __init__(self, token):
        self._token = token
        self._ua_headers = {
            'User-Agent': 'AdsBypasser Monitor',
        }
        self._a_headers = self._ua_headers.copy()
        self._a_headers.update({
            'Authorization': 'token {0}'.format(token),
        })

    @gen.coroutine
    def get_user(self):
        code, user = yield self._a_get('/user')
        return code, user

    @gen.coroutine
    def get_teams(self):
        code, teams = yield self._a_get('/user/teams')
        return code, teams

    @gen.coroutine
    def _a_get(self, path):
        url = 'https://api.github.com{0}'.format(path)
        code, data = yield http_get(url, headers=self._a_headers)
        data = json.loads(data.decode('utf-8'))
        return code, data
