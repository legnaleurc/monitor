import time
import os

from selenium import webdriver

from .base import USERSCRIPT, download, quiting, Runner


USERSCRIPT = 'https://adsbypasser.github.io/releases/adsbypasser.user.js'
GM_URL = 'https://addons.mozilla.org/firefox/downloads/file/282084/greasemonkey-2.3-fx.xpi'
GM_PATH = '/tmp/greasemonkey.xpi'
AUTO_PATH = '/tmp/gmautoinstall.xpi'


class FirefoxRunner(Runner):

    def do_prepare(self):
        if not os.path.exists(GM_PATH):
            download(GM_URL, GM_PATH)

        profile = webdriver.FirefoxProfile()
        profile.add_extension(extension=GM_PATH)
        profile.add_extension(extension=AUTO_PATH)

        with quiting(webdriver.Firefox(firefox_profile=profile)) as driver:
            try:
                driver.get(USERSCRIPT)
            except Exception as e:
                # expected exception: UI thread locked by modal dialog
                pass
            # wait for the dialog disappear
            time.sleep(5)
