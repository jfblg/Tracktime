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
    category_round = db.Column(db.Integer, nullable=True)
    start_line_number = db.Column(db.Integer, nullable=True)

    __table_args__ = (db.UniqueConstraint('category_id', 'participant_id',),)

    def __init__(self, category_id, participant_id):
        self.category_id = category_id
        self.participant_id = participant_id
        self.category_round = None
        self.start_line_number = None


    def json(self):
        return {
                "category_id": self.category_id,
                "participant_id": self.participant_id,
                "category_round": self.category_round,
                "start_line_number": self.start_line_number,
                }

    @classmethod
    def list_all(cls):
        return cls.query.all()
