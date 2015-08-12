from tornado import gen

from monitord.runner import FlavorFactory
from monitord import settings


class Controller(object):

    def __init__(self):
        self._running = False
        self._canceling = False

    @property
    def canceling():
        return self._canceling

    @gen.coroutine
    def queue_test(self):
        if self._running:
            # already running
            print('still running')
            return
        self._running = True
        # TODO read flavor from args
        flavor = FlavorFactory.create('vagrant')
        runners = flavor.create_browsers()
        cases = settings.read_test_cases()
        for runner in runners:
            try:
                yield runner.prepare()
                for name, case in cases.items():
                    for c in case:
                        print('from: {0}'.format(c['from']))
                        print('to: {0}'.format(c['to']))
                        result = yield runner.run(c['from'], c['to'])
                        print(result)
            except Exception as e:
                print(e)
            finally:
                yield runner.close()
        self._running = False
        self._canceling = False

    def cancel_test(self):
        self._canceling = True
