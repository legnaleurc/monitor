# TODO database schema versioning
# TODO decide which tables should be indexed

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


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


class SiteResult(Base):

    __tablename__ = 'site_result'

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer)
    user_script_manager_id = Column(Integer)
    name = Column(String)
