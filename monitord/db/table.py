# TODO decide which tables should be indexed

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean


Base = declarative_base()


class SchemaVersion(Base):

    __tablename__ = 'schema_version'

    id = Column(Integer, primary_key=True)
    version = Column(Integer)


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


class Shell(Base):

    __tablename__ = 'shell'

    id = Column(Integer, primary_key=True)
    browser_id = Column(Integer)
    user_script_manager_id = Column(Integer)
    enabled = Column(Boolean)


class BuildStatus(Base):

    __tablename__ = 'build_status'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    begin_time = Column(Integer)
    end_time = Column(Integer)
    status = Column(String)
    detail = Column(String)


class SiteResult(Base):

    __tablename__ = 'site_result'

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer)
    shell_id = Column(Integer)
    name = Column(String)


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    github_token = Column(String)
    admin = Column(Boolean)
    read = Column(Boolean)
    write = Column(Boolean)
