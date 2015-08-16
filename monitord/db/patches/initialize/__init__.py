import collections
from os.path import op

import yaml

from monitord import db


def create_table():
    md = db.Base.metadata
    print(md)


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
        for name, channels in browsers:
            for channel in channels:
                b = db.Browser(name=name, channel=channel)
                session.add(b)
        for name, channels in user_script_managers:
            for channel in channels:
                usm = db.UserScriptManager(name=name, channel=channel)
                session.add(usm)
        session.flush()
        for usm_name, usm_list in shells:
            for usm_data in usm_list:
                usm_channel = usm_data['channel']
                usm = session.query(db.UserScriptManager).filter(db.UserScriptManager.name == usm_name and db.UserScriptManager.channel == usm_channel).one()
                browser_name = usm_data['browser_name']
                browser_channels = usm_data['browser_channels']
                for browser_channel in browser_channels:
                    b = session.query(db.Browser).filter(db.Browser.name == browser_name and db.Browser.channel == browser_channel).one()
                    s = db.Shell(browser_id=b.id, user_script_manager_id=usm.id, enabled=True)
                    session.add(s)


def upgrade():
    create_table()
    # insert_data()


def downgrade():
    pass
