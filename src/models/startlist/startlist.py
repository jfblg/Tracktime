from sqlalchemy import exc, subquery
from sqlalchemy.orm import aliased, subqueryload

from wtforms import Form, IntegerField, StringField, validators

from src.models.categories.categories import CategoryModel
from src.models.participants.participants import ParticipantModel
from src.common.database import db


class StartlistNameModel(db.Model):
    # SQLAlchemy  table definition
    __tablename__ = "startlist_details"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    startline_count = db.Column(db.Integer, nullable=False)
    startlist_rounds = db.Column(db.Integer, nullable=True)
    measured_flag = db.Column(db.Boolean, unique=False, default=False)
    # TODO add other details like date of creation, name of author, ...

    startlist = db.relationship("StartlistModel",
                                back_populates='startlist_details',
                                cascade="all, delete, delete-orphan")

    def __init__(self, name, startline_count):
        self.name = name
        self.startline_count = startline_count

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "startline_count": self.startline_count,
            "startlist_rounds": self.startlist_rounds

        }

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
    def get_by_id(cls, startlist_id):
        return db.session.query(cls).filter_by(id=startlist_id).one()

    @classmethod
    def list_measured_all(cls):
        return db.session.query(cls).filter_by(measured_flag=True).order_by(StartlistNameModel.id).all()

    @classmethod
    def list_all(cls):
        return cls.query.all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all_rows(cls):
        all_rows = cls.list_all()
        for row in all_rows:
            row.delete_from_db()


class StartlistModel(db.Model):
    # SQLAlchemy table definition
    __tablename__ = "startlist"
    id = db.Column(db.Integer, primary_key=True)
    startlist_id = db.Column(db.Integer, db.ForeignKey('startlist_details.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))
    start_position = db.Column(db.Integer)
    start_round = db.Column(db.Integer)
    time_measured = db.Column(db.Interval, nullable=True)
    # db.PrimaryKeyConstraint('startlist_id', 'category_id', 'participant_id', name='startlist_pk')

    startlist_details = db.relationship("StartlistNameModel", back_populates="startlist")
    category = db.relationship("CategoryModel", back_populates="startlist")
    participants = db.relationship("ParticipantModel", back_populates="startlist")

    __table_args__ = (db.UniqueConstraint('startlist_id','category_id', 'participant_id',),)

    def __init__(self, startlist_id, category_id, participant_id, start_position, start_round):
        self.startlist_id = startlist_id
        self.category_id = category_id
        self.participant_id = participant_id
        self.start_position = start_position
        self.start_round = start_round
        # TODO add time variable
        # TODO add category index number

    def json(self):
        return {
                "startlist_id": self.startlist_id,
                "category_id": self.category_id,
                "participant_id": self.participant_id,
                "start_position": self.start_position,
                "start_round": self.start_round,
                }

    def save_to_db(self):
        """ Save instance to a database

        :return:
        """
        try:
            db.session.add(self)
            db.session.commit()

        except exc.IntegrityError as e:
            db.session().rollback()


    # WORKING - DO NOT TOUCH
    @classmethod
    def get_startlist_by_category(cls, category_id):
        return db.session.query(StartlistModel).\
                filter_by(category_id=category_id).\
                order_by(StartlistModel.participant_id).\
                all()

    # WORKING - DO NOT TOUCH
    @classmethod
    def get_startlist_by_category_with_names(cls, category_id):
        return db.session.query(StartlistModel, ParticipantModel).\
                filter(StartlistModel.participant_id == ParticipantModel.id).\
                filter(StartlistModel.category_id == category_id).\
                order_by(ParticipantModel.id).\
                all()


    @classmethod
    def get_records_by_startlist_id(cls, startlist_name_id):
        return db.session.query(StartlistModel, ParticipantModel).\
                filter(StartlistModel.participant_id == ParticipantModel.id).\
                filter(StartlistModel.startlist_id == startlist_name_id).\
                order_by(StartlistModel.id).\
                all()


    @classmethod
    def get_records_by_startlist_id_order_by_round_position(cls, startlist_name_id):
        return db.session.query(StartlistModel, ParticipantModel). \
            filter(StartlistModel.participant_id == ParticipantModel.id). \
            filter(StartlistModel.startlist_id == startlist_name_id). \
            order_by(StartlistModel.start_round). \
            order_by(StartlistModel.start_position). \
            all()


    @classmethod
    def get_records_by_startlist_id_and_round_number(cls, startlist_name_id, round_number):
        return db.session.query(StartlistModel, ParticipantModel). \
            filter(StartlistModel.participant_id == ParticipantModel.id). \
            filter(StartlistModel.startlist_id == startlist_name_id). \
            filter(StartlistModel.start_round == round_number). \
            order_by(StartlistModel.start_position). \
            all()

    @classmethod
    def get_records_by_startlist_id_order_by_time(cls, startlist_name_id):
        return db.session.query(StartlistModel, ParticipantModel). \
            filter(StartlistModel.participant_id == ParticipantModel.id). \
            filter(StartlistModel.startlist_id == startlist_name_id). \
            order_by(StartlistModel.time_measured). \
            all()


    @classmethod
    def get_by_startlist_id(cls, startlist_id):
        return db.session.query(StartlistModel).filter_by(id=startlist_id).one()


    @classmethod
    def list_all(cls):
        return cls.query.all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all_rows(cls):
        all_rows = cls.list_all()
        for row in all_rows:
            row.delete_from_db()
