import contextlib
import os.path as op
import tempfile
import os
import importlib

from tornado import gen, httpclient, util

from monitord import settings


USERSCRIPT = 'https://adsbypasser.github.io/releases/adsbypasser.user.js'


@contextlib.contextmanager
def quiting(thing):
    try:
        yield thing
    finally:
        thing.quit()


def chunks(readable_object, buffer_size):
    while True:
        chunk = readable_object.read(buffer_size)
        if not chunk:
            break
        yield chunk


@gen.coroutine
def download_to(remote, local, headers=None):
    client = httpclient.AsyncHTTPClient()
    request = httpclient.HTTPRequest(remote, method='GET', headers=headers)
    response = yield client.fetch(request)
    size = 0
    with open(local, 'wb') as fout:
        for chunk in chunks(response.buffer, 65536):
            fout.write(chunk)
            size += len(chunk)
            fout.flush()
    return size


@gen.coroutine
def download_to_stream(remote, stream, headers=None):
    client = httpclient.AsyncHTTPClient()
    request = httpclient.HTTPRequest(remote, method='GET', headers=headers)
    response = yield client.fetch(request)
    size = 0
    for chunk in chunks(response.buffer, 65536):
        stream.write(chunk)
        size += len(chunk)
        stream.flush()
    return size


class FlavorFactory(object):

    _flavors = {}

    @classmethod
    def create(cls, flavor, *args, **kwargs):
        #if flavor not in cls._flavors:
            #return None
        #Flavor = cls._flavors[flavor]
        pkg = util.import_object('monitord.runner.' + flavor)
        return pkg.Flavor(*args, **kwargs)

    def create_browsers(self):
        usms = settings.read_user_script_managers()
        return [self.do_create_browser(usm_name, usm_channel, b_name, b_channel) for usm_name, usm_channel, b_name, b_channel in usms]

    def do_create_browser(self, usm_name, usm_channel, browser_name, browser_channel):
        raise NotImplementedError()


class Mixin(object):

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass


class Runner(Mixin):

    def __init__(self, *args, **kwargs):
        super(Runner, self).__init__(*args, **kwargs)

        self._driver = None

    @gen.coroutine
    def close(self):
        yield super(Runner, self).close()
        if self._driver:
            self._driver.quit()
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

    @gen.coroutine
    def run(self, from_, to):
        if not self._driver:
            return False

        self._driver.get(from_)

        ok = yield self._wait_for_url(to, 10)
        return ok

    def do_prepare(self):
        raise NotImplementedError()

    @gen.coroutine
    def _wait_for_url(self, to_url, timeout):
        interval = 0.5
        while timeout > 0:
            if self._driver.current_url == to_url:
                return True
            timeout -= interval
            yield gen.sleep(interval)
        return False


class TampermonkeyMixin(Mixin):

    def __init__(self, *args, **kwargs):
        super(TampermonkeyMixin, self).__init__(*args, **kwargs)

        self._store_id = {
            'stable': 'dhdgffkkebhmkfjojejmpbldmpobfkfo',
            'beta': 'gcalenpjmijncebpfijmoaglllgpjagf',
        }
        self._store_url_tpl = 'https://clients2.google.com/service/update2/crx?response=redirect&prodversion=40.0&x=id%3D{id}%26installsource%3Dondemand%26uc'
        self._request_header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36',
            'Referer': 'https://chrome.google.com',
        }
        self._crx_path = {
            'stable': op.join(tempfile.gettempdir(), 'tm_stable.crx'),
            'beta': op.join(tempfile.gettempdir(), 'tm_beta.crx'),
        }

    @gen.coroutine
    def close(self):
        yield super(TampermonkeyMixin, self).close()
        for channel, path in self._crx_path.items():
            if op.exists(path):
                os.remove(path)

    @gen.coroutine
    def install_user_script_manager(self, profile, channel):
        crx_path = self._crx_path[channel]
        if not op.exists(crx_path):
            id_ = self._store_id[channel]
            url = self._store_url_tpl.format(id=id_)
            yield download_to(url, crx_path, self._request_header)
        profile.add_extension(extension=crx_path)

    @gen.coroutine
    def install_user_script(self):
        self.driver.get(USERSCRIPT)
        # wait for network
        yield gen.sleep(5)

        # find the confirm tab
        # TODO close tabs
        handles = self.driver.window_handles
        for handle in handles:
            self.driver.switch_to.window(handle)
            if self.driver.current_url.startswith('chrome-extension://'):
                install = self.driver.find_element_by_css_selector('input.install[value$=nstall]')
                install.click()


class GreasemonkeyMixin(Mixin):

    def __init__(self, *args, **kwargs):
        super(GreasemonkeyMixin, self).__init__(*args, **kwargs)

        self._amo_url = {
            '1.x': 'https://addons.mozilla.org/firefox/downloads/file/243212/greasemonkey-1.15-fx.xpi',
            '3.x': 'https://addons.mozilla.org/firefox/downloads/file/331462/greasemonkey-3.3-fx.xpi',
        }
        self._xpi_path = {
            '1.x': op.join(tempfile.gettempdir(), 'gm_1_x.xpi'),
            '3.x': op.join(tempfile.gettempdir(), 'gm_3_x.xpi'),
        }
        self._helper_url = 'https://github.com/legnaleurc/gmautoinstall/raw/master/releases/gmautoinstall.xpi'
        self._helper_path = op.join(tempfile.gettempdir(), 'gmautoinstall.xpi')

    @gen.coroutine
    def close(self):
        yield super(GreasemonkeyMixin, self).close()
        for channel, path in self._xpi_path.items():
            if op.exists(path):
                os.remove(path)
        if op.exists(self._helper_path):
            os.remove(self._helper_path)

    @gen.coroutine
    def install_user_script_manager(self, profile, channel):
        xpi_path = self._xpi_path[channel]
        if not op.exists(xpi_path):
            url = self._amo_url[channel]
            yield download_to(url, xpi_path)
        if not op.exists(self._helper_path):
            yield download_to(self._helper_url, self._helper_path)
        profile.add_extension(extension=xpi_path)
        profile.add_extension(extension=self._helper_path)
        profile.set_preference("extensions.greasemonkey.installDelay", 0);
        profile.update_preferences()

    @gen.coroutine
    def install_user_script(self):
        try:
            self.driver.get(USERSCRIPT)
        except Exception as e:
            # expected exception: UI thread locked by modal dialog
            pass
        # wait for the dialog disappear
        # TODO gmautoinstall should flag when it's finished, to avoid this
        yield gen.sleep(1)
