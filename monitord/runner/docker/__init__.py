from tornado import gen
from selenium import webdriver

from monitord.runner.base import FlavorFactory, Runner, TampermonkeyMixin, GreasemonkeyMixin
from monitord.util import shell_call


class Flavor(FlavorFactory):

    def __init__(self):
        self._browsers = {
            ('chrome', 'stable'): 'CHROME_FLAVOR=stable',
            ('chrome', 'beta'): 'CHROME_FLAVOR=beta',
            ('chrome', 'dev'): 'CHROME_FLAVOR=unstable',
            ('firefox', 'esr'): 'FIREFOX_VERSION=38.0.6',
            ('firefox', 'release'): 'FIREFOX_VERSION=39.0',
            ('firefox', 'beta'): 'FIREFOX_VERSION=39.0',
        }
        self._mapping = {
            'tampermonkey': ChromeTampermonkeyRunner,
            'greasemonkey': FirefoxGreasemonkeyRunner,
        }

    # Override
    def do_create_browser(self, usm_name, usm_channel, browser_name, browser_channel):
        env = self._browsers[browser_name, browser_channel]
        Class = self._mapping[usm_name]
        return Class(env, usm_channel)


class ChromeTampermonkeyRunner(Runner, TampermonkeyMixin):

    def __init__(self, env, usm_channel):
        super(ChromeTampermonkeyRunner, self).__init__()

        self._env = env
        self._usm_channel = usm_channel

    @gen.coroutine
    def do_prepare(self):
        # spawn docker
        # FIXME it will not leave, use add_callback
        yield shell_call([
            'docker', 'run',
            '--rm',
            '--name=browser',
            '-p=127.0.0.1:4444:24444',
            '-e', self._env,
            'elgalu/selenium:latest',
        ])

        profile = webdriver.ChromeOptions()
        yield self.install_user_script_manager(profile, self._usm_channel)

        self.driver = webdriver.Remote(browser_profile=profile, desired_capabilities=DesiredCapabilities.CHROME)

        # Tampermonkey may not ready yet
        yield gen.sleep(5)
        yield self.install_user_script()


class FirefoxGreasemonkeyRunner(Runner, GreasemonkeyMixin):

    def __init__(self, env, usm_channel):
        super(FirefoxGreasemonkeyRunner, self).__init__()

        self._env = env
        self._usm_channel = usm_channel

    @gen.coroutine
    def do_prepare(self):
        # spawn docker
        # FIXME it will not leave, use add_callback
        yield shell_call([
            'docker', 'run',
            '--rm',
            '--name=browser',
            '-p=127.0.0.1:4444:24444',
            '-e', self._env,
            'elgalu/selenium:latest',
        ])

        profile = webdriver.FirefoxProfile()
        yield self.install_user_script_manager(profile, self._usm_channel)

        self.driver = webdriver.Remote(browser_profile=profile, desired_capabilities=DesiredCapabilities.FIREFOX)

        yield self.install_user_script()
