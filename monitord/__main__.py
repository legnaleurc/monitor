#! /usr/bin/env python3

import os
import sys

from tornado import ioloop, web, log

from monitord.webui import view, api
from monitord import settings
from monitord import core


def main(args=None):
    if args is None:
        args = sys.argv

    setup_logger()

    main_loop = ioloop.IOLoop.instance()

    ctlr = core.Controller()

    opts = {
        'static_path': os.path.join(settings.MODULE_ROOT, 'webui/static'),
        'debug': True,
        'controller': ctlr,
    }
    application = web.Application([
        (r'/', view.RootHandler),
        (r'/api/v1/run', api.RunHandler),
    ], **opts)

    application.listen(8000)

    main_loop.start()

    return 0


def setup_logger():
    log.enable_pretty_logging()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
