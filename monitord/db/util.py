import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tornado import util as t_util

from monitord.db import table
from monitord import settings


def create_engine_from_settings():
    database = settings.DATABASE
    if database['engine'] == 'sqlite':
        if not database['name']:
            dsn = 'sqlite://'
        else:
            dsn = 'sqlite:///{name}'.format(**database)
    else:
        dsn = '{engine}://{username}:{password}@{host}:{port}/{name}'.format(**database)
    return create_engine(dsn)


engine = create_engine_from_settings()
# add session class
Session = sessionmaker(bind=engine)


@contextlib.contextmanager
def scoped():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_current_schema_version():
    table.SchemaVersion.metadata.create_all(engine)
    with scoped() as session:
        sv = session.query(table.SchemaVersion).order_by(table.SchemaVersion.id.desc()).first()
        if sv is None:
            sv = table.SchemaVersion(version=0)
            session.add(sv)
        return sv.version


def migrate():
    patches = [
        'initialize',
    ]
    code_version = len(patches)
    database_version = get_current_schema_version()
    if code_version == database_version:
        # nothing to do
        return
    elif code_version > database_version:
        # need upgrade
        for i in range(database_version, code_version):
            patch = t_util.import_object('monitord.db.patches.' + patches[i])
            patch.upgrade()
    else:
        # need downgrade
        for i in range(database_version, code_version):
            patch = t_util.import_object('monitord.db.patches.' + patches[i])
            patch.downgrade()

    with scoped() as session:
        sv = table.SchemaVersion(version=code_version)
        session.add(sv)
