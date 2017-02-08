import os

from threading import Thread
# TODO how to run while loop and Flask at the same time?
# http://stackoverflow.com/questions/23100704/running-infinite-loops-using-threads-in-python?answertab=votes#tab-top

from flask import Flask, render_template, session
from src.models.timedb.timy import Timy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///timetrack.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "justSom3Kei"

@app.before_first_request
def create_table():
    ''' SQLAlchemy creates the tables it sees from the imports above.
    '''
    db.create_all()
    db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

from src.models.participants.views import participants_blueprint
from src.models.categories.views import categories_blueprint
from src.models.startlist.views import startlist_blueprint
from src.models.timedb.views import timedb_blueprint
# add another models

app.register_blueprint(participants_blueprint, url_prefix="/participants")
app.register_blueprint(categories_blueprint, url_prefix="/categories")
app.register_blueprint(startlist_blueprint, url_prefix="/startlist")
app.register_blueprint(timedb_blueprint, url_prefix="/timedb")
# register another blueprints


if __name__ == "__main__":
    from src.common.database import db
    db.init_app(app)
    app.run(port=4999, debug=True)