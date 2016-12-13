from sqlalchemy import exc
from wtforms import Form, IntegerField, StringField, validators

from src.models.categories.categories import CategoryModel
from src.models.participants.participants import ParticipantModel
from src.common.database import db


class StartlistModel(db.Model):
    # SQLAlchemy table definition
    __tablename__ = "startlist"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship("CategoryModel", backref="categories")
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))
    participant = db.relationship("ParticipantModel", backref="participants")
    start_position = db.Column(db.Integer)
    start_round = db.Column(db.Integer)

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

    @classmethod
    def join_startlist(cls, category_id):
        return db.session.query(StartlistModel, CategoryModel, ParticipantModel).\
                filter(cls.category_id == CategoryModel.id).\
                filter(cls.participant_id == ParticipantModel.id). \
                order_by(cls.id).\
                all()

    @classmethod
    def join_experiment(cls, category_id):
        return db.session.query(StartlistModel)\
                .join(StartlistModel.category_id)\
                .options(contains_eager(StartlistModel.category_id))\
                .filter(StartlistModel.category_id == category_id)

    @classmethod
    def get_startlist_by_category_join_participants(cls, category_id):
        return cls.query.filter_by(category_id=category_id)

    @classmethod
    def list_all(cls):
        return cls.query.all()
