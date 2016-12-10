from src.app import app
from src.common.database import db

db.init_app(app)

@app.before_first_request
def create_table():
    ''' SQLAlchemy creates the tables it sees from the imports above.
    '''
    db.create_all()