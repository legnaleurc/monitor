from tornado import process, gen


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@gen.coroutine
def shell_call(args):
    p = process.Subprocess(args)
    exit_code = yield p.wait_for_exit()
    return exit_code
