import contextlib

import requests


USERSCRIPT = 'https://adsbypasser.github.io/releases/adsbypasser.user.js'


@contextlib.contextmanager
def quiting(thing):
    try:
        yield thing
    finally:
        thing.quit()


def download(remote, local, headers=None):
    r = requests.get(url=remote, headers=headers, stream=True)
    size = 0
    with open(local, 'wb') as fout:
        for chunk in r.iter_content(8192):
            fout.write(chunk)
            size += len(chunk)
            fout.flush()
    return size


def Runner(object):

    def __init__(self):
        pass

    def prepare(self):
        self.do_prepare()
