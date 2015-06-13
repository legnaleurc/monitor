import os
from monitord.runner import browsers

TMP = 'tmp'
cases = [
    ('http://linkbucks.com/BXHk/url/92b96ad805273519f7b83349e855b6296666e0cf77334c7c5606777aebde100db5b6f44e8dc30b', 'http://www.keeplinks.eu/p/5472c60b831fa'),
]

def working_directory():
    if not os.path.exists(TMP):
        os.makedirs(TMP)
    os.chdir(TMP)

working_directory()

for browser in browsers:
    browser.prepare()
    for case in cases:
        result = browser.run(case[0], case[1])
        print(result)
    browser.close()
