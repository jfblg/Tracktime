import os

from flask import Flask, render_template

from src.common.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///timetrack.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "justSom3Kei"

@app.before_first_request
def create_table():
    ''' SQLAlchemy creates the tables it sees from the imports above.
    '''
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

from src.models.participants.views import participants_blueprint
from src.models.categories.views import categories_blueprint
# add another models

app.register_blueprint(participants_blueprint, url_prefix="/signup")
app.register_blueprint(categories_blueprint, url_prefix="/categories")
# register another blueprints


if __name__ == "__main__":
    from src.common.database import db
    db.init_app(app)
    app.run(port=4999, debug = True)
