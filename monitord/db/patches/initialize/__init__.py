import collections
import os.path as op

import yaml
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean

from monitord import db
from monitord.db import util as db_util


def create_table():
    metadata = MetaData()
    browser = Table('browser', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('channel', String),
    )
    user_script_manager = Table('user_script_manager', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('channel', String),
    )
    shell = Table('shell', metadata,
        Column('id', Integer, primary_key=True),
        Column('browser_id', Integer),
        Column('user_script_manager_id', Integer),
        Column('enabled', Boolean),
    )
    build_status = Table('build_status', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer),
        Column('begin_time', Integer),
        Column('end_time', Integer),
        Column('status', String),
        Column('detail', String),
    )
    site_result = Table('site_result', metadata,
        Column('id', Integer, primary_key=True),
        Column('build_id', Integer),
        Column('shell_id', Integer),
        Column('name', String),
    )
    user = Table('user', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String, unique=True),
        Column('github_token', String),
        Column('admin', Boolean),
        Column('read', Boolean),
        Column('write', Boolean),
    )
    metadata.create_all(db_util.engine)


def insert_data():
    path = op.dirname(__file__)

    with open(op.join(path, 'browsers.yaml'), 'r') as fin:
        browsers = yaml.safe_load(fin)
        browsers = collections.OrderedDict(sorted(browsers.items(), key=lambda __: __[0]))
    with open(op.join(path, 'user_script_managers.yaml'), 'r') as fin:
        user_script_managers = yaml.safe_load(fin)
        user_script_managers = collections.OrderedDict(sorted(user_script_managers.items(), key=lambda __: __[0]))
    with open(op.join(path, 'shells.yaml'), 'r') as fin:
        shells = yaml.safe_load(fin)
        shells = collections.OrderedDict(sorted(shells.items(), key=lambda __: __[0]))

    with db.scoped() as session:
        for name, channels in browsers.items():
            for channel in channels:
                b = db.Browser(name=name, channel=channel)
                session.add(b)
        for name, channels in user_script_managers.items():
            for channel in channels:
                usm = db.UserScriptManager(name=name, channel=channel)
                session.add(usm)
        session.flush()
        for usm_name, usm_list in shells.items():
            for usm_data in usm_list:
                usm_channel = usm_data['channel']
                usm = session.query(db.UserScriptManager).filter(db.UserScriptManager.name == usm_name, db.UserScriptManager.channel == usm_channel).one()
                browser_name = usm_data['browser_name']
                browser_channels = usm_data['browser_channels']
                for browser_channel in browser_channels:
                    b = session.query(db.Browser).filter(db.Browser.name == browser_name, db.Browser.channel == browser_channel).one()
                    s = db.Shell(browser_id=b.id, user_script_manager_id=usm.id, enabled=True)
                    session.add(s)


def upgrade():
    create_table()
    insert_data()


def downgrade():
    pass
