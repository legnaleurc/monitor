import time
import os

from selenium import webdriver

from .base import USERSCRIPT, download, Runner


GM_URL = 'https://addons.mozilla.org/firefox/downloads/file/282084/greasemonkey-2.3-fx.xpi'
GM_EXT = '/tmp/greasemonkey.xpi'
AUTO_URL = 'https://github.com/legnaleurc/gmautoinstall/raw/master/releases/gmautoinstall.xpi'
AUTO_EXT = '/tmp/gmautoinstall.xpi'


class FirefoxRunner(Runner):

    def __init__(self):
        super(FirefoxRunner, self).__init__()

    def do_prepare(self):
        if not os.path.exists(GM_EXT):
            download(GM_URL, GM_EXT)
        if not os.path.exists(AUTO_EXT):
            download(AUTO_URL, AUTO_EXT)

        profile = webdriver.FirefoxProfile()
        profile.add_extension(extension=GM_EXT)
        profile.add_extension(extension=AUTO_EXT)
        profile.set_preference("extensions.greasemonkey.installDelay", 0);

        self.driver = webdriver.Firefox(firefox_profile=profile)

        try:
            self.driver.get(USERSCRIPT)
        except Exception as e:
            # expected exception: UI thread locked by modal dialog
            pass
        # wait for the dialog disappear
        # TODO gmautoinstall should flag when it's finished, to avoid this
        time.sleep(1)
