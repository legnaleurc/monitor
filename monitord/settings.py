import os.path as op

import yaml


MODULE_ROOT = op.dirname(__file__)
COOKIE_SECRET = None
DATABASE = None
GITHUB = None
HTTP_PORT = None


def read_test_cases():
    path = op.join(MODULE_ROOT, '../sites.yaml')
    with open(path, 'r') as fin:
        data = yaml.safe_load(fin)
    return data


def _read():
    global COOKIE_SECRET
    global DATABASE
    global GITHUB
    global HTTP_PORT
    path = op.join(MODULE_ROOT, '../settings.yaml')
    with open(path, 'r') as fin:
        data = yaml.safe_load(fin)
        COOKIE_SECRET = data['cookie_secret']
        DATABASE = data['database']
        GITHUB = data['github']
        HTTP_PORT = data['http_port']


_read()
