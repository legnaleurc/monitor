from tornado import gen

from monitord.runner import FlavorFactory
from monitord import settings, util


class Controller(object):

    def __init__(self):
        self._running = False
        self._canceling = False
        self._logger = util.get_logger()

    @property
    def canceling():
        return self._canceling

    @gen.coroutine
    def queue_test(self):
        if self._running:
            # already running
            self._logger.warn('still running')
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
                        self._logger.info('from: {0}'.format(c['from']))
                        self._logger.info('to: {0}'.format(c['to']))
                        result = yield runner.run(c['from'], c['to'])
                        self._logger.info(result)
            except Exception as e:
                self._logger.exception('catched exception')
            finally:
                yield runner.close()
        self._running = False
        self._canceling = False
        self._logger.info('done testing')

    def cancel_test(self):
        self._canceling = True
