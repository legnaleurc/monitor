import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# TODO read setting
engine = create_engine('sqlite:////tmp/monitord.sqlite')
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
