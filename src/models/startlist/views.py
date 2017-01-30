from flask import Blueprint, request, render_template, session, redirect, url_for
from src.models.categories.categories import CategoryModel, CategoryAddForm
from src.models.startlist.startlist import StartlistModel, StartlistNameModel
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
    plus_session_counter()
    return redirect(url_for('startlist.wizard'))


@startlist_blueprint.route('/create_wizard', methods=['GET', 'POST'])
def wizard_start():
    startlist_display = [(st.id, st.name) for st in StartlistNameModel.list_all()]
    return render_template('startlist/create_new_wizard.html', data=startlist_display)


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
    init_session_counter()

    if session['counter'] > startlist_instance.startlist_rounds:
        clearsession()
        return redirect(url_for('.wizard_start'))

    found_records = [record for record in StartlistModel.get_records_by_startlist_id_and_round_number(
        startlist_selected,
        session['counter']
    )]

    startlist_round = []
    for stm, ptm in found_records:
        record = (ptm.last_name, ptm.first_name, stm.start_position, stm.start_round)
        startlist_round.append(record)

    progress_now = session['counter'] * 100 / startlist_instance.startlist_rounds
    progress_now_int = int(round(progress_now))

    # print(startlist1.name)
    # print(startlist1.startline_count)
    # print(startlist1.startlist_rounds)

    return render_template(
        'startlist/wizard.html',
        name=startlist_instance.name,
        startlist=startlist_round,
        progress_now=progress_now_int
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
    # Uncomment to re-process the start list. Working only when the start list is empty.
    output = []
    categories = [(cat_id, cat_name) for cat_id, cat_name in CategoryModel.list_categories_ordered()]

    for cat_id, cat_name in categories:
        output_emb = list()
        output_emb.append(cat_name)

        cat_participants_names = [(start_table, part_table) for start_table, part_table in
                                  StartlistModel.get_startlist_by_category_with_names(cat_id)]
        output_emb.append(cat_participants_names)

        output.append(output_emb)

    return render_template('startlist/results_1run.html', data=output)


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


@startlist_blueprint.route('/create', methods=['GET'])
def create_startlist():
    defined_categories = [(category.id, category.category_name) for category in CategoryModel.list_all()]
    return render_template('startlist/create_new_list.html', categories=defined_categories)


@startlist_blueprint.route('/startlist_created', methods=['POST'])
def generate():
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

    # TODO zobraz zoznam startujucich v novovytvorenom liste

    return redirect(url_for('.create_startlist'))


@startlist_blueprint.route('/time', methods=['GET', 'POST'])
def time_random():
    random_times = []

    seconds = round(random.uniform(10.0, 60.0), 4)
    random_times.append("12:{0}".format(seconds))

    seconds = round(random.uniform(10.0, 60.0), 4)
    random_times.append("13:{0}".format(seconds))

    seconds = round(random.uniform(10.0, 60.0), 4)
    random_times.append("14:{0}".format(seconds))

    seconds = round(random.uniform(10.0, 60.0), 4)
    random_times.append("15:{0}".format(seconds))

    print(random_times)

    if request.method == 'POST':
        pass

    return render_template('startlist/time.html', random_times=random_times)
