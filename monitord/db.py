from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()


class SiteResult(Base):

    __tablename__ = 'site_result'

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer)
    name = Column(String)
    result = Column(String)
