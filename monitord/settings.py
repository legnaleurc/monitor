import os.path as op

import yaml


MODULE_ROOT = op.dirname(__file__)


def read_test_cases():
    path = op.join(MODULE_ROOT, '../sites.yaml')
    with open(path, 'r') as fin:
        data = yaml.safe_load(fin)
    return data


def read_github():
    path = op.join(MODULE_ROOT, '../github.yaml')
    with open(path, 'r') as fin:
        data = yaml.safe_load(fin)
    return data
