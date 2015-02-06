from runner import browsers


cases = [
    ('http://linkbucks.com/BXHk/url/92b96ad805273519f7b83349e855b6296666e0cf77334c7c5606777aebde100db5b6f44e8dc30b', 'http://www.keeplinks.eu/p/5472c60b831fa'),
]


for browser in browsers:
    browser.prepare()
    for case in cases:
        result = browser.run(case[0], case[1])
        print(result)
    browser.close()
