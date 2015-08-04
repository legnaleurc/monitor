import os.path as op


MODULE_ROOT = op.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'sqlite',
        'NAME': 'default.sqlite',
    },
}
