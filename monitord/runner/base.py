import contextlib
import time

from tornado import gen
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
        return [self.do_create_browser(usm_name, usm_channel, b_name, b_channel) for usm_name, usm_channel, b_name, b_channel in usms]

    def do_create_browser(self, usm_name, usm_channel, browser_name, browser_channel):
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

    @gen.coroutine
    def prepare(self):
        yield gen.maybe_future(self.do_prepare())

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
