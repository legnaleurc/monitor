from tornado import gen

from monitord.runner import FlavorFactory
from monitord import settings


class Controller(object):

    def __init__(self):
        pass

    @gen.coroutine
    def queue_test(self):
        # TODO leave if already running
        # TODO read flavor from args
        flavor = FlavorFactory.create('docker')
        runners = flavor.create_browsers()
        cases = settings.read_test_cases()
        for browser in runners:
            try:
                yield browser.prepare()
                for name, case in cases.items():
                    for c in case:
                        result = yield browser.run(c['from'], case['to'])
                        print(result)
            finally:
                yield gen.maybe_future(browser.close())
