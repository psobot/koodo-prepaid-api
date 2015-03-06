import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, DateTime

default_connection_string = 'sqlite:///./koodo.db'
connection_string = os.environ.get(
    'DATABASE_URL', default_connection_string
)
engine = create_engine(connection_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class LogEntry(Base):
    __tablename__ = 'log_entries'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime())
    minutes_remaining = Column(Float(32))
    mb_remaining = Column(Float(32))

    def __init__(self, time=None, minutes_remaining=None, mb_remaining=None):
        self.time = time
        self.minutes_remaining = minutes_remaining
        self.mb_remaining = mb_remaining

    def __repr__(self):
        return '<LogEntry %r>' % (self.time)

    def to_object(self):
        return {
            "at": self.time.isoformat(),
            "minutes_remaining": self.minutes_remaining,
            "mb_remaining": self.mb_remaining,
        }

Base.metadata.create_all(bind=engine)
