from sqlalchemy import exc
from wtforms import Form, IntegerField, StringField, validators

from src.common.database import db


class CategoryAddForm(Form):
    category_name = StringField('Category name', [
        validators.Length(min=1, max=40),
        validators.DataRequired(message="Required")])

    gender = StringField('Gender', [
        validators.Length(min=2, max=10),
        validators.data_required(message="Required")])

    year_start = IntegerField('Start year', [
        validators.NumberRange(min=1917, max=2099),
        validators.data_required(message="Required. Please specify number between 1917 and 2017.")])

    year_end = IntegerField('End year', [
        validators.NumberRange(min=1917, max=2099),
        validators.data_required(message="Required. Please specify number between 1917 and 2017.")])


class CategoryModel(db.Model):
    # SQLAlchemy table definition
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    year_start = db.Column(db.Integer, nullable=False)
    year_end = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('category_name', 'gender', 'year_start', 'year_end'),)

    startlist = db.relationship("StartlistModel",
                             back_populates='category',
                             cascade="all, delete, delete-orphan")


    # Foreign key definition. For the future
    # store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    # store = db.relationship('StoreModel')

    def __init__(self, category_name, gender, year_start, year_end):
        self.category_name = category_name
        self.gender = gender
        self.year_start = int(year_start)
        self.year_end = int(year_end)

    def json(self):
        return {
                "category_name": self.category_name,
                "gender": self.gender,
                "year_start": self.year_start,
                "year_end": self.year_end
                }

    def save_to_db(self):
        ''' Function does update and insert to the DB (upserting)
        '''
        # SQLAlchemy can translate object into the row

        try:
            db.session.add(self)
            db.session.commit()

        except exc.IntegrityError as e:
            db.session().rollback()

    @classmethod
    def find_by_id(cls, category_id):
        return db.session.query(cls).filter_by(id=category_id).one()

    @classmethod
    def list_categories_ordered(cls):
        return db.session.query(CategoryModel.id, CategoryModel.category_name).\
                order_by(CategoryModel.id).\
                all()

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


