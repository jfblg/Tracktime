import os
from src.config import UPLOAD_FOLDER_NAME
from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.participants.participants import ParticipantModel, RunnerRegistrationForm
from src.models.participants.mass_import_xls import MassImport
from werkzeug.utils import secure_filename

# Not all imports from above are actually used.
# They are listed for your reference.

participants_blueprint = Blueprint("participants", __name__)

UPLOAD_FOLDER = '/path/to/the/uploads'


@participants_blueprint.route('/add', methods=['GET', 'POST'])
def add():
    form = RunnerRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        gender = request.form['gender']
        year = request.form['year'].strip()

        runner = ParticipantModel(first_name=first_name.title(),
                                  last_name=last_name.title(),
                                  gender=gender.lower(),
                                  year=year, )
        runner.save_to_db()
        return render_template('participants/signup_success.html',
                               first_name=runner.first_name,
                               last_name=runner.last_name,
                               gender=runner.gender,
                               year=runner.year,
                               form=form)

    return render_template('participants/signup.html', form=form)


@participants_blueprint.route('/list', methods=['GET', 'POST'])
def list():
    # Not used at the moment
    if request.method == 'POST':
        year_filter = request.form['year'].strip()
        if year_filter != "":
            # found = RunnerModel.find_by_year(year_filter)
            filtered = [runner.json() for runner in ParticipantModel.find_by_year(year_filter)]
            return render_template('participants/registered.html', data=filtered)

    registered = [runner.json() for runner in ParticipantModel.list_all()]
    registered_count = len(registered)

    return render_template('participants/registered.html', data=registered, registered_count=registered_count)


@participants_blueprint.route('/import', methods=['GET', 'POST'])
def mass_import():
    """
    It is anticipated that the file format is OK.
    """
    # TODO implement file format check.

    if request.method == 'POST':

        # check if the post request has the file part
        if 'InputFile' not in request.files:
            return render_template('participants/mass_import.html')

        file = request.files['InputFile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return render_template('participants/mass_import_no_file_selected.html')

        if file and MassImport.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filefolder = os.path.join(os.path.dirname(os.getcwd()), UPLOAD_FOLDER_NAME)
            abs_path = os.path.join(filefolder, filename)
            file.save(abs_path)

            if MassImport.insert_many(abs_path):
                # success import
                return render_template('participants/mass_import_success.html')
            else:
                # invalid file path
                return render_template('participants/mass_import_failed.html')

    return render_template('participants/mass_import.html')

