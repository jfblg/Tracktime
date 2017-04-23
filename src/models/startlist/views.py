from flask import Blueprint, request, render_template, session, redirect, url_for
from src.models.categories.categories import CategoryModel, CategoryAddForm
from src.models.startlist.startlist import StartlistModel, StartlistNameModel
from src.models.timedb.timedb import TimeDbModel
from src.models.timedb.timydb import TimyDbModel
import src.models.startlist.startlist_processing as startlist_processing
from sqlalchemy import Time

import time
import datetime
import random

import pprint

startlist_blueprint = Blueprint('startlist', __name__)


@startlist_blueprint.route('/', methods=['GET', 'POST'])
def startlist():
    # Uncomment to re-process the start list. Working only when the start list is empty.
    # process(4)
    output = []

    # print(time.gmtime(0))
    # print(time.time())
    # print(time.clock())
    # time_d = datetime.datetime.now() - datetime.timedelta(hours=24)
    # print(datetime.timedelta(hours=1, minutes=15, milliseconds=1456))
    #
    # time1 = datetime.datetime.strptime('12:34.43', '%M:%S.%f')
    # time2 = datetime.datetime.strptime('12:34.4332', '%M:%S.%f')
    # print(time1 < time2)

    startlists = [startlist_def for startlist_def in StartlistNameModel.list_all()]

    output = {}

    for st in startlists:
        stlist_records = StartlistModel.get_records_by_startlist_id(st.id)
        records_list = []
        for ST, PT in stlist_records:
            save_obj_tup = (PT.last_name, PT.first_name, ST.start_round, ST.start_position)
            records_list.append(save_obj_tup)

        output[st.name] = records_list

    return render_template('startlist/startlist.html', data=output)


@startlist_blueprint.route('/next', methods=['GET', 'POST'])
def next_round():

    if request.method == "POST":
        received_values = []
        for index in range(0, len(session['random_times'])):
            received_values.append(request.form[str(index)])

        received_values = [int(value) for value in received_values]
        results_possition = dict(zip(received_values, session['random_times']))

        results_id = []
        for _, _, start_position, _, startlist_id in session['startlist_round']:
            result_tuple = (startlist_id, results_possition[start_position])
            results_id.append(result_tuple)

        for startlist_id, time_measured in results_id:
            found_runner = StartlistModel.get_by_startlist_id(startlist_id)
            found_runner.time_measured = convert_time_to_delta(time_measured)
            found_runner.save_to_db()

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
    startlist_display = [(st.id, st.name) for st in StartlistNameModel.list_all()]
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
    random_times = time_random(startlist_lines)

    # loading of the times from old database
    # db_times = [str(item.time_measured)[2:-4] for item in TimeDbModel.list_all()][-startlist_lines:]
    # session['random_times'] = db_times

    # loading of the times from the external database
    db_times_ext = [str(item.time_measured)[2:-4] for item in TimyDbModel.list_all()][-startlist_lines:]
    session['random_times'] = db_times_ext

    progress_now = session['counter'] * 100 / startlist_instance.startlist_rounds
    progress_now_int = int(round(progress_now))

    # print(startlist1.name)
    # print(startlist1.startline_count)
    # print(startlist1.startlist_rounds)

    return render_template(
        'startlist/wizard.html',
        name=startlist_instance.name,
        startlist=startlist_round,
        progress_now=progress_now_int,
        startlist_lines=startlist_lines,
        random_times=db_times_ext
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
    return render_template('startlist/results_finished_startlists.html', data=startlist_finished)


@startlist_blueprint.route('/result_startlist', methods=['POST'])
def results_specific_startlist():
    startlist_id = request.form['startlist_select']
    startlist_instance = StartlistNameModel.get_by_id(startlist_id)

    result_records = [result for result in StartlistModel.get_records_by_startlist_id_order_by_time(startlist_id)]

    output_list = []
    for st, pt in result_records:
        result_item = (pt.last_name, pt.first_name, st.time_measured)
        output_list.append(result_item)


    return render_template('startlist/results_specific_startlist.html',
                           startlist_name=startlist_instance.name,
                           data=output_list)


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


@startlist_blueprint.route('/startlist_created', methods=['POST'])
def generate_startlist_category():
    if request.method == 'POST':
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


def time_random(number_of_random_times):
    random_times = []

    for minutes in range(10, 10+int(number_of_random_times)):
        seconds = round(random.uniform(10.0, 60.0), 4)
        random_times.append("{0}:{1}".format(minutes, seconds))

    return random_times
