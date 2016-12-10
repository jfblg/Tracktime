from wtforms import Form, BooleanField, StringField, PasswordField, validators

from src.common.database import db


class RunnerRegistrationForm(Form):
    first_name = StringField('First name', [
        validators.Length(min=4, max=25),
        validators.DataRequired(message="Required")
    ])

    last_name = StringField('Last name', [
        validators.Length(min=4, max=25)])

    email_addr = StringField('Email address',[
        validators.Length(min=6, max=35),
        validators.data_required(message="Required")
    ])

    year = StringField('Year of birth', [
        validators.Length(min=2, max=4),
        validators.data_required(message="Required")
    ])


class RunnerModel(db.Model):
    # SQLAlchemy table definition
    __tablename__ = "participants"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email_addr = db.Column(db.String(100))
    year = db.Column(db.Integer)

    # Foreign key definition. For the future
    # store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    # store = db.relationship('StoreModel')

    def __init__(self, first_name, last_name, email_addr, year):
        self.first_name = first_name
        self.last_name = last_name
        self.email_addr = email_addr
        self.year = year

    def json(self):
        return {"first_name": self.first_name,
                "last_name": self.last_name,
                "email_addr": self.email_addr,
                "year": self.year
                }

    @classmethod
    def find_by_last_name(cls, last_name):
        # 'guery' is a SQLAlchemy query builder
        # SELECT FROM items WHERE name=name LIMIT 1
        # returned data gets converted into ItemModel object
        return cls.query.filter_by(last_name=last_name).first()

    def save_to_db(self):
        ''' Function does update and insert to the DB (upserting)
        '''
        # SQLAlchemy can translate object into the row
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
