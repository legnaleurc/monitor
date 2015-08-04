from monitord.runner import FlavorFactory


class Controller(object):

    def __init__(self):
        pass

    def queue_test(self):
        # TODO leave if already running
        flaver = FlavorFactory.create('docker')
        for browser in flaver.bowsers:
            browser.prepare()
            for case in cases:
                result = browser.run(case[0], case[1])
                print(result)
            browser.close()
