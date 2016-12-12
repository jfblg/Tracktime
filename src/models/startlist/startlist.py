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
    def join_startlist(cls):
        # return db.session.query(StartlistModel, CategoryModel, ParticipantModel)\
        #     .join(CategoryModel)\
        #     .join(ParticipantModel)\
        #     .filter(CategoryModel.id == cls.category_id)\
        #     .filter(ParticipantModel == cls.participant_id)\
        #      .order_by(CategoryModel.id)\
        #      .order_by(ParticipantModel.id)\
        #      .all()
        #
        #     return db.session.query(StartlistModel)\
        #         .join(CategoryModel)\
        #         .join(ParticipantModel)\
        #         .options(
        #             db.contains_eager(StartlistModel.start_position)\
        #             .db.contains_eager(CategoryModel.category_name)\
        #             .db.contains_eager(ParticipantModel.first_name)
        #         )\
        #         .filter(CategoryModel.id == cls.category_id)\
        #         .all()
        #
        # q = Session.query(User, Document, DocumentPermissions).filter(User.email == Document.author). \
        #     filter(Document.name == DocumentPermissions.document). \
        #     filter(User.email == 'someemail').all()
        return db.session.query(StartlistModel, CategoryModel).\
                filter(CategoryModel.id == cls.category_id).\
                all()

    @classmethod
    def list_all(cls):
        return cls.query.all()
