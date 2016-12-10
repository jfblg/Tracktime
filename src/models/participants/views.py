from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.participants.participants import RunnerModel, RunnerRegistrationForm

# Not all imports from above are actually used.
# They are listed for your reference.

participants_blueprint = Blueprint("participants", __name__)

@participants_blueprint.route('/', methods=['GET', 'POST'])
def index():
    form = RunnerRegistrationForm(request.form)
    print(form.validate())
    if request.method == 'POST' and form.validate():
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_addr = request.form['email_addr']
        year = request.form['year']

        runner = RunnerModel(first_name=first_name, last_name=last_name, email_addr=email_addr, year=year)
        runner.save_to_db()
        return render_template('participants/signup_success.jinja2',
                               first_name=first_name,
                               last_name=last_name,
                               year=year,
                               form=form
                               )

    return render_template('participants/signup.jinja2', form=form)

