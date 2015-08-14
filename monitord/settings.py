import os.path as op

import yaml


MODULE_ROOT = op.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'sqlite',
        'NAME': 'default.sqlite',
    },
}


def read_test_cases():
    path = op.join(MODULE_ROOT, '../sites.yaml')
    with open(path, 'r') as fin:
        data = yaml.safe_load(fin)
    return data


def read_user_script_managers():
    path = op.join(MODULE_ROOT, '../user_script_managers.yaml')
    with open(path, 'r') as fin:
        data = yaml.safe_load(fin)
    for usm_name, usm_packs in data.items():
        for usm_pack in usm_packs:
            usm_channel = usm_pack['channel']
            b_name = usm_pack['browser']['name']
            b_channel = usm_pack['browser']['channel']
            yield usm_name, usm_channel, b_name, b_channel


def read_github():
    path = op.join(MODULE_ROOT, '../githug.yaml')
    with open(path, 'r') as fin:
        data = yaml.safe_load(fin)
    return data
