from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.participants.participants import ParticipantModel, RunnerRegistrationForm
import src.models.participants.mass_import_xls as mass_import

# Not all imports from above are actually used.
# They are listed for your reference.

participants_blueprint = Blueprint("participants", __name__)

@participants_blueprint.route('/add', methods=['GET', 'POST'])
def add():
    # TODO - rework later. Add import from file functionality
    mass_import.insert_many()

    form = RunnerRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        email_addr = request.form['email_addr'].strip()
        gender = request.form['gender'].strip()
        year = request.form['year'].strip()

        runner = ParticipantModel(first_name=first_name.title(),
                                  last_name=last_name.title(),
                                  gender=gender.lower(),
                                  year=year,
                                  email_addr=email_addr.lower())
        runner.save_to_db()
        return render_template('participants/signup_success.html',
                                first_name=runner.first_name,
                                last_name=runner.last_name,
                                gender = runner.gender,
                                year=runner.year,
                                email_addr=runner.email_addr,
                                form=form)

    return render_template('participants/signup.html', form=form)


@participants_blueprint.route('/list', methods=['GET', 'POST'])
def list():
    if request.method == 'POST':
        year_filter = request.form['year'].strip()
        if year_filter != "":
            # found = RunnerModel.find_by_year(year_filter)
            filtered = [runner.json() for runner in ParticipantModel.find_by_year(year_filter)]
            return render_template('participants/registered.html', data=filtered)

    registered = [runner.json() for runner in ParticipantModel.list_all()]
    return render_template('participants/registered.html', data=registered)
