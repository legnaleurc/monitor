# TODO database schema versioning
# TODO decide which tables should be indexed

import contextlib

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Browser(Base):

    __tablename__ = 'browser'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    channel = Column(String)


class UserScriptManager(Base):

    __tablename__ = 'user_script_manager'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    channel = Column(String)
    browser_id = Column(Integer)
    enabled = Column(Boolean)


class BuildStatus(Base):

    __tablename__ = 'build_status'

    id = Column(Integer, primary_key=True)
    user = Column(Integer)
    begin_time = Column(Integer)
    end_time = Column(Integer)
    status = Column(String)


class SiteResult(Base):

    __tablename__ = 'site_result'

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer)
    user_script_manager_id = Column(Integer)
    name = Column(String)

class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    github_token = Column(String)
    admin = Column(Boolean)
    read = Column(Boolean)
    write = Column(Boolean)


def _create_session_class():
    engine = create_engine('sqlite:////tmp/monitord.sqlite')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


Session = _create_session_class()


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
