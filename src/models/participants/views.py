from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.participants.participants import RunnerModel, RunnerRegistrationForm
from src.models.participants.mass_import_xls import insert_many
from src.common.database import db

# Not all imports from above are actually used.
# They are listed for your reference.

participants_blueprint = Blueprint("participants", __name__)

@participants_blueprint.route('/', methods=['GET', 'POST'])
def index():
    insert_many()
    form = RunnerRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        email_addr = request.form['email_addr'].strip()
        gender = "male"
        year = request.form['year'].strip()

        runner = RunnerModel(first_name=first_name.title(),
                             last_name=last_name.title(),
                             email_addr=email_addr.lower(),
                             gender=gender,
                             year=year)
        runner.save_to_db()
        return render_template('participants/signup_success.html',
                                first_name=runner.first_name,
                                last_name=runner.last_name,
                                year=runner.year,
                                form=form)

    return render_template('participants/signup.html', form=form)


@participants_blueprint.route('/registered', methods=['GET'])
def show_registered():
    registered = [runner.json() for runner in RunnerModel.list_all()]
    return render_template('participants/registered.html', data=registered)


# @app.errorhandler(AssertionError)
# def handle_sqlalchemy_assertion_error(err):
#     return make_response(standard_response(None, 400, err.message), 400)