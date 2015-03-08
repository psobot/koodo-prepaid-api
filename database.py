import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, DateTime, Date, String

default_connection_string = 'sqlite:///./koodo.db'

connection_string = os.environ.get(
    'DATABASE_URL', os.environ.get(
        'CLEARDB_DATABASE_URL',
        default_connection_string
    )
)

# MySQLdb doesn't like this option, but ClearDB provides it.
connection_string = connection_string.replace('?reconnect=true', '')

engine = create_engine(connection_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class UsageDataPoint(Base):
    __tablename__ = 'usage_data_points'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    minutes_remaining = Column(Float(32))
    mb_remaining = Column(Float(32))

    def to_object(self):
        return {
            "at": self.time.isoformat(),
            "minutes_remaining": self.minutes_remaining,
            "mb_remaining": self.mb_remaining,
        }


class KoodoTransaction(Base):
    __tablename__ = 'koodo_transactions'
    id = Column(Integer, primary_key=True)
    koodo_id = Column(Integer)
    date = Column(Date)
    description = Column(String(255))
    credit = Column(Integer)
    debit = Column(Integer)

    def to_object(self):
        return {
            "date": self.date.isoformat(),
            "description": self.description,
            "credit": self.credit,
            "debit": self.debit,
        }

Base.metadata.create_all(bind=engine)
