from sqlalchemy import Column, Integer, Interval
from sqlalchemy.ext.declarative import declarative_base

from src.common.ext_db import Database

Base = declarative_base()

class TimyDbModel(Base):
    # TODO add function to delete all times from the table
    # TODO add also column - time and date created

    __tablename__ = 'timetable'
    id = Column(Integer, primary_key=True)
    time_measured = Column(Interval, nullable=False)
    order_number = Column(Integer, nullable=False)  # number received from TIMY3 [1-99]

    session = Database.initialize()

    def __init__(self, time_measured, order_number):
        self.time_measured = time_measured
        self.order_number = order_number

    @classmethod
    def list_all(cls):
        print(cls.session)
        return cls.session.query(cls).all()




