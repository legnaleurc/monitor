#! /usr/bin/env python3

import os
import sys

from tornado import ioloop, web, log

from monitord.webui import view, api
from monitord import settings, core, util


def main(args=None):
    if args is None:
        args = sys.argv

    util.setup_logger()

    main_loop = ioloop.IOLoop.instance()

    ctlr = core.Controller()

    opts = {
        'static_path': os.path.join(settings.MODULE_ROOT, 'webui/static'),
        'debug': True,
        'controller': ctlr,
        'cookie_secret': 'TODO: change me',
    }
    application = web.Application([
        (r'/', view.RootHandler),
        (r'/api/v1/run', api.RunHandler),
        (r'/api/v1/cancel', api.CancelHandler),
        (r'/login', api.LoginHandler),
    ], **opts)

    application.listen(8000)

    main_loop.start()

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
