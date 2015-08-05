import contextlib
import time

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


class FlavorFactory(object):

    _flavors = {}

    @classmethod
    def create(cls, flavor, *args, **kwargs):
        if flavor not in cls._flavors:
            return None
        Flavor = cls._flavors[flavor]
        return Flavor(*args, **kwargs)

    def create_browsers(self):
        return self.do_create_browsers()

    def do_create_browsers(self):
        raise NotImplementedError()


class Runner(object):

    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, driver):
        self._driver = driver

    def prepare(self):
        self.do_prepare()

    def close(self):
        self._driver.quit()

    def run(self, from_, to):
        if not self._driver:
            return False

        self._driver.get(from_)
        time.sleep(10)
        return self._driver.current_url == to

    def do_prepare(self):
        raise NotImplementedError()
