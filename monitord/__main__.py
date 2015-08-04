#! /usr/bin/env python3

import os
import sys

from tornado import ioloop, web, log

from monitord.webui import view
from monitord import settings


def main(args=None):
    if args is None:
        args = sys.argv

    setup_logger()

    main_loop = ioloop.IOLoop.instance();

    opts = {
        'static_path': os.path.join(settings.MODULE_ROOT, 'webui/static'),
        'debug': True,
    }
    application = web.Application([
        (r'/', view.RootHandler),
    ], **opts)

    application.listen(8000)

    main_loop.start()

    return 0


def setup_logger():
    log.enable_pretty_logging()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
