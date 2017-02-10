from src.common.database import db
from sqlalchemy import exc


class TimeDbModel(db.Model):
    # SQLAlchemy  table definition
    # TODO add function to delete all times from the table
    # TODO add also column - time and date created

    __tablename__ = "timetable"

    id = db.Column(db.Integer, primary_key=True)
    time_measured = db.Column(db.Interval, nullable=False)
    order_number = db.Column(db.Integer, nullable=False) # number received from TIMY3 [1-99]

    def __repr__(self):
        return "<TimeDbModel(time_measured='%s', order='%s')>" % (self.time_measured, self.order_number)

    def json(self):
        return {
            "id": self.id,
            "time_measured": str(self.time_measured)[:-4],
            "order_number": self.order_number
        }

    def __init__(self, time_measured, order_number):
        self.time_measured = time_measured
        self.order_number = order_number

    def save_to_db(self):
        """ Save instance to a database

        :return:
        """
        try:
            db.session.add(self)
            db.session.commit()

        except exc.IntegrityError as e:
            db.session().rollback()

    @classmethod
    def get_by_id(cls, timedb_id):
        return db.session.query(cls).filter_by(id=timedb_id).one()

    @classmethod
    def list_all(cls):
        return cls.query.all()