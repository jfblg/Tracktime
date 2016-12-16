from sqlalchemy import exc, subquery
from sqlalchemy.orm import aliased, subqueryload

from wtforms import Form, IntegerField, StringField, validators

from src.models.categories.categories import CategoryModel
from src.models.participants.participants import ParticipantModel
from src.common.database import db


class StartlistModel(db.Model):
    # SQLAlchemy table definition
    __tablename__ = "startlist"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))
    start_position = db.Column(db.Integer)
    start_round = db.Column(db.Integer)

    category = db.relationship("CategoryModel", back_populates="startlist")
    participants = db.relationship("ParticipantModel", back_populates="startlist")

    __table_args__ = (db.UniqueConstraint('category_id', 'participant_id',),)

    def __init__(self, category_id, participant_id, start_position, start_round):
        self.category_id = category_id
        self.participant_id = participant_id
        self.start_position = start_position
        self.start_round = start_round
        # TODO add time variable
        # TODO add category index number

    def json(self):
        return {
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
        return db.session.query(StartlistModel).filter_by(category_id=category_id).order_by(StartlistModel.participant_id).all()

    # WORKING - DO NOT TOUCH
    @classmethod
    def get_startlist_by_category_with_names(cls, category_id):
        return db.session.query(StartlistModel, ParticipantModel).\
                filter(StartlistModel.participant_id == ParticipantModel.id).\
                filter(StartlistModel.category_id == category_id).\
                order_by(ParticipantModel.id).\
                all()


    @classmethod
    def list_all(cls):
        return cls.query.all()
