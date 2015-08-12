import subprocess as sp
import signal
import re
import os
import shlex
import os.path as op

from tornado import gen, process, ioloop, iostream
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from monitord.runner.base import FlavorFactory, Runner, TampermonkeyMixin, GreasemonkeyMixin
from monitord import settings


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


class VagrantRunner(Runner):

    def __init__(self, browser_name, browser_channel, usm_channel):
        super(VagrantRunner, self).__init__()

        self._browser_name = browser_name
        self._browser_channel = browser_channel
        self._usm_channel = usm_channel

        self._container_id = None
        self._container_logger = None
        self._loop = ioloop.IOLoop.current()
        self._notifiers = {}

    @gen.coroutine
    def close(self):
        yield super(VagrantRunner, self).close()
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
        p = self._spawn_vagrant_process([
            '/vagrant/stop_container.sh', self._container_id,
        ], quiet=True)

        ok = yield gen.Task(self._stop_container)
        exit_code = yield p.wait_for_exit()

        return ok and exit_code == 0

    def _stop_container(self, callback):
        if self._container_id is None:
            callback(False)
            return
        self._notifiers['stop'] = callback
        print('killed, wait for exit ...')

    @gen.coroutine
    def _spawn_container(self):
        p = self._spawn_vagrant_process([
            '/vagrant/start_container.sh', self._browser_name, self._browser_channel,
        ])
        output = yield p.stdout.read_until_close()
        exit_code = yield p.wait_for_exit()
        self._container_id = output.decode('utf-8').strip()

        self._container_logger = self._spawn_vagrant_process([
            'docker', 'logs', '-f', self._container_id,
        ])
        while True:
            try:
                chunk = yield self._container_logger.stdout.read_bytes(65536, partial=True)
                self._parse_container_output(chunk.decode('utf-8'))
            except iostream.StreamClosedError:
                break
        try:
            exit_code = yield self._container_logger.wait_for_exit()
            self._notify('stop', True)
            return exit_code
        except sp.CalledProcessError as e:
            self._notify('stop', False)
            return -1

    def _parse_container_output(self, chunk):
        print(chunk)
        if re.search(r'Selenium Server is up and running', chunk) is not None:
            self._notify('start', True)

    def _to_vagrant_ssh(self, cmd_list):
        cmd = map(shlex.quote, cmd_list)
        cmd = ' '.join(cmd)
        return [
            'vagrant', 'ssh',
            '-c', cmd,
            '--',
            '-q',
        ]

    def _spawn_vagrant_process(self, cmd_list, quiet=False):
        out_flag = process.Subprocess.STREAM if not quiet else sp.DEVNULL
        return process.Subprocess(self._to_vagrant_ssh(cmd_list), stdout=out_flag, stderr=sp.STDOUT, cwd=op.join(settings.MODULE_ROOT, '../env/vagrant'))


class ChromeTampermonkeyRunner(VagrantRunner, TampermonkeyMixin):

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


class FirefoxGreasemonkeyRunner(VagrantRunner, GreasemonkeyMixin):

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
