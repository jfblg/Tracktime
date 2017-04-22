import src.common.constants

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DbAbsLayer(object):

    def createSession(self):
        Session = sessionmaker()
        self.session = Session.configure(bind=self.engine)


class Database(object):

    Base = declarative_base()

    @staticmethod
    def initialize(db_uri="sqlite:////Users/ferojanus/Repos/timy_database/db1.sqlite"):
        engine = create_engine(db_uri)
        Database.Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.configure(bind=engine)
        # session = DBSession()
        return DBSession()

    @staticmethod
    def insert():
        pass

    @staticmethod
    def update():
        pass

    @staticmethod
    def delete():
        pass