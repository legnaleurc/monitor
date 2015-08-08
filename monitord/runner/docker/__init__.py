import subprocess as sp
import signal
import re
import os

from tornado import gen, process, ioloop, iostream
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from monitord.runner.base import FlavorFactory, Runner, TampermonkeyMixin, GreasemonkeyMixin


class Flavor(FlavorFactory):

    def __init__(self):
        self._mapping = {
            ('chrome', 'tampermonkey'): ChromeTampermonkeyRunner,
            ('firefox', 'greasemonkey'): FirefoxGreasemonkeyRunner,
        }

    # Override
    def do_create_browser(self, usm_name, usm_channel, browser_name, browser_channel):
        Class = self._mapping[browser_name, usm_name]
        return Class(browser_name, browser_channel, usm_channel)


class DockerRunner(Runner):

    def __init__(self, browser_name, browser_channel, usm_channel):
        super(DockerRunner, self).__init__()

        self._browser_name = browser_name
        self._browser_channel = browser_channel
        self._usm_channel = usm_channel

        self._container = None
        self._loop = ioloop.IOLoop.current()
        self._notifiers = {}

    @gen.coroutine
    def close(self):
        super(DockerRunner, self).close()
        # FIXME is it possible to wait until closed
        yield self.stop_container()

    def _notify(self, topic, *args, **kwargs):
        if topic not in self._notifiers:
            return
        notifier = self._notifiers[topic]
        notifier(*args, **kwargs)
        del self._notifiers[topic]

    @gen.coroutine
    def start_container(self):
        ok = yield gen.Task(self._start_container)
        return ok

    def _start_container(self, callback):
        self._notifiers['start'] = callback
        self._loop.add_callback(self._spawn_container)

    @gen.coroutine
    def stop_container(self):
        ok = yield gen.Task(self._stop_container)
        return ok

    def _stop_container(self, callback):
        if not self._container or not self._container.proc:
            callback(False)
            return
        self._notifiers['stop'] = callback
        os.kill(self._container.proc.pid, signal.SIGINT)

    @gen.coroutine
    def _spawn_container(self):
        self._container = process.Subprocess([
            'docker', 'run',
            '--rm',
            '-p=127.0.0.1:4444:4444',
            '-e', 'BROWSER_NAME={0}'.format(self._browser_name),
            '-e', 'BROWSER_CHANNEL={0}'.format(self._browser_channel),
            'wcpan/monitor:latest',
        ], stdout=process.Subprocess.STREAM, stderr=sp.STDOUT)

        while True:
            try:
                chunk = yield self._container.stdout.read_bytes(65536, partial=True)
                self._parse_container_output(chunk.decode('utf-8'))
            except iostream.StreamClosedError:
                break
        try:
            exit_code = yield self._container.wait_for_exit()
            self._notify('stop', True)
            return exit_code
        except sp.CalledProcessError as e:
            self._notify('stop', False)
            return -1

    def _parse_container_output(self, chunk):
        print(chunk)
        if re.search(r'Selenium Server is up and running', chunk) is not None:
            self._notify('start', True)


class ChromeTampermonkeyRunner(DockerRunner, TampermonkeyMixin):

    def __init__(self, browser_name, browser_channel, usm_channel):
        super(ChromeTampermonkeyRunner, self).__init__(browser_name, browser_channel, usm_channel)

    @gen.coroutine
    def do_prepare(self):
        ok = yield self.start_container()
        if not ok:
            raise Exception('what?')

        profile = webdriver.ChromeOptions()
        yield self.install_user_script_manager(profile, self._usm_channel)

        caps = DesiredCapabilities.CHROME.copy()
        caps.update(profile.to_capabilities())
        self.driver = webdriver.Remote(desired_capabilities=caps)

        # Tampermonkey may not ready yet
        yield gen.sleep(5)
        yield self.install_user_script()


class FirefoxGreasemonkeyRunner(DockerRunner, GreasemonkeyMixin):

    def __init__(self, browser_name, browser_channel, usm_channel):
        super(FirefoxGreasemonkeyRunner, self).__init__(browser_name, browser_channel, usm_channel)

    @gen.coroutine
    def do_prepare(self):
        ok = yield self.start_container()
        if not ok:
            raise Exception('what?')

        profile = webdriver.FirefoxProfile()
        yield self.install_user_script_manager(profile, self._usm_channel)

        self.driver = webdriver.Remote(browser_profile=profile, desired_capabilities=DesiredCapabilities.FIREFOX)

        yield self.install_user_script()
