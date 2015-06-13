import time
from urllib.parse import urlparse
import platform
import sys
import os
import zipfile
import stat

import requests
from selenium import webdriver

from .base import USERSCRIPT, download, Runner


CHROME_DRIVER_META_URL = 'http://chromedriver.storage.googleapis.com/LATEST_RELEASE'
CHROME_DRIVER_URL = 'http://chromedriver.storage.googleapis.com/{version}/chromedriver_{os}.zip'
CHROME_STORE_URL = 'https://clients2.google.com/service/update2/crx?response=redirect&prodversion=40.0&x=id%3D{id}%26installsource%3Dondemand%26uc'
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36',
    'Referer': 'https://chrome.google.com',
}

CD_ZIP = 'chromedriver.zip'
TM_ID = 'dhdgffkkebhmkfjojejmpbldmpobfkfo'
TM_EXT = 'tampermonkey.crx'


def get_version():
    r = requests.get(url=CHROME_DRIVER_META_URL)
    return r.text


def driver_url(version):
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == 'linux':
        name = 'linux64' if machine == 'x86_64' else 'linux32'
        return CHROME_DRIVER_URL.format(os=name, version=version)
    if system == 'darwin':
        return CHROME_DRIVER_URL.format(os='mac32', version=version)
    if system == 'windows' or system.startswith('cygwin'):
        return CHROME_DRIVER_URL.format(os='win32', version=version)

    # Default behavior
    return None


def driver_executable():
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        return 'chromedriver.exe'

    # Default behavior
    return 'chromedriver'


class ChromeRunner(Runner):

    def __init__(self):
        super(ChromeRunner, self).__init__()

    def do_prepare(self):
        CD_EXEC = driver_executable()
        if not os.path.exists(CD_EXEC):
            version = get_version()
            download(driver_url(version), CD_ZIP)
            archive = zipfile.ZipFile(CD_ZIP);
            archive.extract(CD_EXEC)
            os.chmod(CD_EXEC, stat.S_IXUSR)
        if not os.path.exists(TM_EXT):
            download(CHROME_STORE_URL.format(id=TM_ID), TM_EXT, headers=REQUEST_HEADERS)

        profile = webdriver.ChromeOptions()
        profile.add_extension(extension=TM_EXT)

        self.driver = webdriver.Chrome(executable_path=CD_EXEC, chrome_options=profile)

        # Tampermonkey may not ready yet
        time.sleep(5)
        self.driver.get(USERSCRIPT)
        time.sleep(5)

        # find the confirm tab
        # TODO close tabs
        handles = self.driver.window_handles
        for handle in handles:
            self.driver.switch_to.window(handle)
            if self.driver.current_url.startswith('chrome-extension://'):
                install = self.driver.find_element_by_css_selector('input.install[value$=nstall]')
                install.click()
