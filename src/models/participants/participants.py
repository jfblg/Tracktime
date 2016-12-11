from wtforms import Form, BooleanField, IntegerField, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField


from src.common.database import db
from sqlalchemy import exc


class RunnerRegistrationForm(Form):
    first_name = StringField('First name', [
        validators.Length(min=2, max=25),
        validators.DataRequired(message="Required")])

    last_name = StringField('Last name', [
        validators.Length(min=2, max=25)])


    email_addr = EmailField('Email address',[
        validators.Length(min=6, max=35),
        validators.data_required(message="Required")])

    gender = StringField('Gender', [
        validators.Length(min=2, max=6),
        validators.data_required(message="Required. 'boy' or 'girl'")])

    year = IntegerField('Year of birth', [
        validators.NumberRange(min=1917, max=2017),
        validators.data_required(message="Required. Please specify number between 1917 and 2017.")])


class ParticipantModel(db.Model):
    # SQLAlchemy table definition
    __tablename__ = "participants"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email_addr = db.Column(db.String(100))
    gender = db.Column(db.String(6))
    year = db.Column(db.Integer)
    __table_args__ = (db.UniqueConstraint('first_name',
                                       'last_name',
                                       'year'),)


    # Foreign key definition. For the future
    # store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    # store = db.relationship('StoreModel')

    def __init__(self, first_name, last_name, gender, year, email_addr):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.year = int(year)
        self.email_addr = email_addr

    def json(self):
        return {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "gender": self.gender,
                "year": self.year,
                "email_addr": self.email_addr
                }

    @classmethod
    def find_by_year(cls, year):
        # 'guery' is a SQLAlchemy query builder
        # SELECT FROM items WHERE name=name LIMIT 1
        # returned data gets converted into ItemModel object
        return cls.query.filter_by(year=int(year))

    @classmethod
    def find_by_gender_and_year(cls, gender, year):
        return cls.query.filter_by(gender=gender, year=year)

    def save_to_db(self):
        ''' Function does update and insert to the DB (upserting)
        '''
        # SQLAlchemy can translate object into the row

        try:
            db.session.add(self)
            db.session.commit()

        except exc.IntegrityError as e:
            db.session().rollback()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def list_all(cls):
        return cls.query.all()


