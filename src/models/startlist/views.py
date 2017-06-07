from flask import Blueprint, request, render_template, session, redirect, url_for
from src.models.categories.categories import CategoryModel, CategoryAddForm
from src.models.startlist.startlist import StartlistModel, StartlistNameModel
from src.models.timedb.timedb import TimeDbModel
from src.models.timedb.timydb import TimyDbModel
import src.models.startlist.startlist_processing as startlist_processing
import src.models.startlist.startlist_alg as startlist_alg
from sqlalchemy import Time

import time
import datetime
import random

from pprint import pprint as pp

startlist_blueprint = Blueprint('startlist', __name__)


@startlist_blueprint.route('/', methods=['GET', 'POST'])
def startlist():
    output, output_length = startlist_processing.get_startlist_all_frontend()

    return render_template('startlist/startlist_all.html', data=output, length=output_length)


@startlist_blueprint.route('/list_all', methods=['GET', 'POST'])
def startlist_menu():
    startlist_all = [(stlist.id, stlist.name) for stlist in StartlistNameModel.list_all()]
    return render_template('startlist/startlist_one_menu.html', data=startlist_all)


@startlist_blueprint.route('/startlist_one', methods=['POST'])
def startlist_one():
    startlist_id = request.form['startlist_select']
    startlist_instance = StartlistNameModel.get_by_id(startlist_id)

    output_list = startlist_processing.startlist_generate(startlist_id)
    output_length = startlist_processing.startlist_generate_length(startlist_id)

    return render_template('startlist/startlist_one.html',
                           startlist_name=startlist_instance.name,
                           data=output_list,
                           length=output_length)

@startlist_blueprint.route('/list_all_edit', methods=['GET', 'POST'])
def startlist_menu_edit():
    startlist_all = [(stlist.id, stlist.name) for stlist in StartlistNameModel.list_all()]
    return render_template('startlist/startlist_one_menu_edit.html', data=startlist_all)


@startlist_blueprint.route('/startlist_one_edit', methods=['POST'])
def startlist_one_edit():
    startlist_id = request.form['startlist_select']

    # for startlist_one_edit_save()
    session['startlist_id'] = startlist_id

    startlist_instance = StartlistNameModel.get_by_id(startlist_id)
    output_list = startlist_processing.startlist_generate(startlist_id)
    output_length = startlist_processing.startlist_generate_length(startlist_id)
    rounds, line_count = startlist_processing.startlist_get_rounds_lines(startlist_id)

    return render_template('startlist/startlist_one_edit.html',
                           startlist_name=startlist_instance.name,
                           data=output_list,
                           length=output_length,
                           rounds=rounds,
                           line_count=line_count)


@startlist_blueprint.route('/startlist_one_edit_save', methods=['POST'])
def startlist_one_edit_save():
    startlist_id = session['startlist_id']
    new_values = startlist_processing.parse_request_form(request.form)
    startlist_processing.update_startlist_records(startlist_id, new_values)

    return redirect(url_for('startlist.startlist_menu_edit'))


@startlist_blueprint.route('/next', methods=['GET', 'POST'])
def next_round():

    if request.method == "POST":

        # Note: Verification if the received values are unique.
        # There cannot be 2 times assigned to the same starting line
        if startlist_processing.wizard_input_verification(request.form) is False:
            # used to let the 'startlist.wizard' know, which template should be generated
            session['wrong_entry'] = 1
            return redirect(url_for('startlist.wizard'))

        results_possition = startlist_processing.wizard_process_received_form(request.form)

        # print("Results tuple:")
        # print(results_possition)
        # print()

        results_id = []
        for _, _, start_position, _, startlist_id in session['startlist_round']:
            # print("Start position: {}".format(start_position))
            # print("Start startlist_id: {}".format(startlist_id))

            result_tuple = (startlist_id, results_possition[start_position])
            results_id.append(result_tuple)

        for startlist_id, time_measured in results_id:
            # print("ST.ID: {}  --- TIME: {}".format(startlist_id, time_measured))
            found_runner = StartlistModel.get_by_startlist_id(startlist_id)

            # if an athlete doesn't finish, the DNF may be entered.
            # he will then be assigned max time possible to enter
            # because of his high time, he will be also listed at the end in results.

            if time_measured in "DNF dnf".split():
                time_measured = "59:59.59"

            try:
                found_runner.time_measured = convert_time_to_delta(time_measured)
                found_runner.save_to_db()
            except ValueError:
                session['wrong_entry'] = 2
                return redirect(url_for('startlist.wizard'))

    plus_session_counter()
    return redirect(url_for('startlist.wizard'))


def convert_time_to_delta(time_entered):
    epoch = datetime.datetime.utcfromtimestamp(0)

    time_entered = time_entered.strip()
    datetime_composite = "1 Jan 1970 {}".format(time_entered)
    time_converted = datetime.datetime.strptime(datetime_composite, '%d %b %Y %M:%S.%f')
    delta_time = time_converted - epoch
    return delta_time


@startlist_blueprint.route('/create_wizard', methods=['GET', 'POST'])
def wizard_start():
    # clearing session counter
    clearsession()
    startlist_display = [(st.id, st.name) for st in StartlistNameModel.list_all() if not st.measured_flag]
    return render_template('startlist/create_new_wizard.html', data=startlist_display)


@startlist_blueprint.route('/get_times', methods=['POST'])
def get_times_from_db():
    position = request.form.get('position', '0', type=int)
    times = [item for item in TimeDbModel.list_all()]
    print(position)
    print(times)
    return "Hello World"

@startlist_blueprint.route('/wizard', methods=['GET', 'POST'])
def wizard():

    if request.method == 'POST':
        try:
            session['startlist_selected'] = request.form['startlist_select']
        except:
            print("error - method wizard")

    try:
        startlist_selected = session['startlist_selected']
    except KeyError:
        return redirect(url_for('.wizard_start'))

    startlist_instance = StartlistNameModel.get_by_id(startlist_selected)

    # it does nothing if session['counter'] already exists
    init_session_counter()

    if session['counter'] > startlist_instance.startlist_rounds:
        # indicates that there are times stored in this startlist
        startlist_instance.measured_flag = True
        startlist_instance.save_to_db()
        return redirect(url_for('.wizard_start'))

    found_records = [record for record in StartlistModel.get_records_by_startlist_id_and_round_number(
        startlist_selected,
        session['counter']
    )]

    startlist_round = []
    for stm, ptm in found_records:
        record = (ptm.last_name, ptm.first_name, stm.start_position, stm.start_round, stm.id)
        startlist_round.append(record)

    # to easily receive startlist_id in the next_round()
    session['startlist_round'] = startlist_round

    startlist_lines = len(startlist_round)

    # not used at the moment
    # random_times = time_random(startlist_lines)

    # loading of the times from old database
    # db_times = [str(item.time_measured)[2:-4] for item in TimeDbModel.list_all()][-startlist_lines:]
    # session['random_times'] = db_times

    # loading of the times from the external database
    db_times_ext = [str(item.time_measured)[2:-4] for item in TimyDbModel.list_all()][-startlist_lines:]
    session['random_times'] = db_times_ext

    progress_now = session['counter'] * 100 / startlist_instance.startlist_rounds
    progress_now_int = int(round(progress_now))

    # Note: Verification if the site has been reloaded due to wrong assignment of startlines by user.
    # redirected from next_round() function.
    try:
        if session['wrong_entry'] == 1:
            session['wrong_entry'] = 0

            return render_template(
                'startlist/wizard_wrong_lines_assigned.html',
                name=startlist_instance.name,
                startlist=startlist_round,
                progress_now=progress_now_int,
                startlist_lines=startlist_lines,
                random_times=db_times_ext,
                rounds_count=startlist_instance.startlist_rounds
                )

        if session['wrong_entry'] == 2:
            session['wrong_entry'] = 0

            return render_template(
                'startlist/wizard_wrong_time_entered.html',
                name=startlist_instance.name,
                startlist=startlist_round,
                progress_now=progress_now_int,
                startlist_lines=startlist_lines,
                random_times=db_times_ext,
                rounds_count=startlist_instance.startlist_rounds
                )

    except KeyError:
        pass

    return render_template(
        'startlist/wizard.html',
        name=startlist_instance.name,
        startlist=startlist_round,
        progress_now=progress_now_int,
        startlist_lines=startlist_lines,
        random_times=db_times_ext,
        rounds_count=startlist_instance.startlist_rounds
    )


@startlist_blueprint.route('/clear')
def clearsession():
    # Clear the session
    session.clear()
    return True


def init_session_counter():
    try:
        session['counter']
    except KeyError:
        session['counter'] = 1


def plus_session_counter():
    try:
        session['counter'] += 1
    except KeyError:
        session['counter'] = 1


def minus_session_counter():
    try:
        session['counter'] -= 1
    except KeyError:
        session['counter'] = 1


@startlist_blueprint.route('/results', methods=['GET', 'POST'])
def results():
    startlist_finished = [(stlist.id, stlist.name) for stlist in StartlistNameModel.list_measured_all()]
    return render_template('startlist/results_finished_startlists_menu.html', data=startlist_finished)


@startlist_blueprint.route('/result_startlist', methods=['POST'])
def results_specific_startlist():
    startlist_id = request.form['startlist_select']

    startlist_instance = StartlistNameModel.get_by_id(startlist_id)
    output_list = startlist_processing.result_list_generate(startlist_id)

    return render_template('startlist/results_specific_startlist.html',
                           startlist_name=startlist_instance.name,
                           data=output_list)


@startlist_blueprint.route('/results_all', methods=['GET'])
def results_all():
    data = startlist_processing.results_all()
    return render_template('startlist/results_finished_startlists.html', data=data)


@startlist_blueprint.route('/findrunner', methods=['GET', 'POST'])
def find_runner():
    # NOT USED AT THE MOMENT
    return render_template('startlist/find_runner.html')


@startlist_blueprint.route('/addtime', methods=['GET', 'POST'])
def add_time():
    if request.method == 'POST':
        # TODO add time to DB
        try:
            user_id = int(request.form['participant'])
            time_entered = request.form['time'].strip()
            datetime_composite = "1 Jan 1970 {}".format(time_entered)
            time_converted = datetime.datetime.strptime(datetime_composite, '%d %b %Y %M:%S.%f')
        except ValueError:
            return render_template('startlist/add_time_wrong.html')

        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = time_converted - epoch
        print(delta)

        found_runner = StartlistModel.get_by_participant_id(user_id)

        found_runner.time_measured = delta
        found_runner.save_to_db()

        return render_template('startlist/add_time_added.html', time=time_converted)

    return render_template('startlist/add_time.html')


@startlist_blueprint.route('/create_category', methods=['GET'])
def create_startlist_category():
    defined_categories = [(category.id, category.category_name) for category in CategoryModel.list_all()]
    return render_template('startlist/create_new_list_category.html', categories=defined_categories)


@startlist_blueprint.route('/startlist_created_cat', methods=['POST'])
def generate_startlist_category():
    if request.method == 'POST':
        print(request.form)
        startlist_name = request.form['startlist_name'].strip()
        startlist_lines = request.form['startlist_lines']
        startlist_category = request.form['startlist_category']

        # print(startlist_name)
        # print(startlist_lines)
        # print(startlist_category)

        new_startlist = StartlistNameModel(startlist_name, startlist_lines)
        new_startlist.save_to_db()

        print("Startlist ID: {} - {} - {}".format(new_startlist.id, new_startlist.name, new_startlist.startline_count))

        new_startlist.startlist_rounds = startlist_processing.process(
            new_startlist.id,
            startlist_category,
            int(startlist_lines)
        )
        new_startlist.save_to_db()

    return redirect(url_for('.create_startlist_category'))


@startlist_blueprint.route('/create_classification', methods=['GET'])
def create_startlist_classification():
    # TODO pass number of athletes in each finished startlist to the template.

    startlist_finished = [(stlist.id, stlist.name) for stlist in StartlistNameModel.list_measured_all()]

    return render_template('startlist/create_new_list_classification.html', startlist_finished=startlist_finished)


@startlist_blueprint.route('/startlist_created_class', methods=['POST'])
def generate_startlist_classfication():
    if request.method == 'POST':
        # print(request.form)

        startlist_finished_id = request.form['startlist_select']
        startlist_name = request.form['startlist_name'].strip()
        startlist_top_times = int(request.form['startlist_top_times'])
        startlist_lines = request.form['startlist_lines']

        new_startlist = StartlistNameModel(startlist_name, startlist_lines)
        new_startlist.save_to_db()

        # Note: Not used at the moment
        # startlist_finished_instance = StartlistNameModel.get_by_id(startlist_finished_id)

        startlist_finished_results_ordered = \
            [result for result in StartlistModel.get_records_by_startlist_id_order_by_time(startlist_finished_id)]\
            [:startlist_top_times]

        print(startlist_finished_results_ordered)

        # removing Participant objects from a tuples
        # removing Participant objects from a tuples
        # and also ignoring Athletes with the time 59:59.59 - datetime.timedelta(0, 3599, 590000)
        # 59:59.59 means that an athletes is DNF. This form of time has been chosen for code simplicity.
        # At the UZE sprinter event, it is impossible that an athlete will have such a time
        startlist_finished_only_results_ordered = \
            [startlist_record for startlist_record, _ in startlist_finished_results_ordered
                if startlist_record.time_measured != datetime.timedelta(0, 3599, 590000)]

        # In case there is only one classification run, the records are re-ordered so that the fasterst
        # athletes are placed in the middle of the start field.
        if startlist_top_times <= int(startlist_lines):
            startlist_finished_only_results_ordered = startlist_alg.order_from_the_middle(startlist_finished_only_results_ordered)

        # generating new startlist record instances, startline numbers and rounds assignment
        new_startlist.startlist_rounds = startlist_processing.process_classification(
            new_startlist.id,
            startlist_finished_only_results_ordered,
            int(startlist_lines)
        )
        new_startlist.save_to_db()

    return redirect(url_for('.create_startlist_classification'))




def time_random(number_of_random_times):
    random_times = []

    for minutes in range(10, 10+int(number_of_random_times)):
        seconds = round(random.uniform(10.0, 60.0), 4)
        random_times.append("{0}:{1}".format(minutes, seconds))

    return random_times
