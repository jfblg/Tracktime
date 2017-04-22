from datetime import datetime, timedelta
import json

from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from src.models.timedb.timydb import TimyDbModel

timedb_blueprint = Blueprint('timedb', __name__)


@timedb_blueprint.route('/', methods=['GET', 'POST'])
def list():

    output = [(item.id, str(item.time_measured), item.order_number) for item in TimyDbModel.list_all()]
    position = 4

    if request.method == 'POST':
        requested = request.form['position']
        position = int(requested)
    output = output[-position:]

    return render_template('timedb/timetable.html', output=to_json(output))

def to_json(table_data):
    """ Transforms list of tuples to json. The output must be serialized in order to use AJAX.
    """
    return [tuple_to_dict(t) for t in table_data]


def tuple_to_dict(t):
    return {"id": t[0],
            "time": t[1],
            "order_number": t[2]}


@timedb_blueprint.route('/_last_x_times', methods=['POST'])
def get_last_x():
    output = [(item.id, str(item.time_measured)[:-4], item.order_number) for item in TimeDbModel.list_all()]
    # output = [item.json() for item in TimeDbModel.list_all()]
    position = request.form.get('position',0, type=int)
    # print(position)
    output = output[-position:]
    # print(output)

    # print(request.form['username'])
    # return jsonify(result=result)
    return render_template('timedb/timetable.html', data=output)
    # return "abc"
    # # return jsonify(result=output)

@timedb_blueprint.route('/_ajax_reload_table')
def relaod_table():
    output = [(item.id, str(item.time_measured), item.order_number) for item in TimyDbModel.list_all()]
    position = 4
    output = output[-position:]

    return render_template('timedb/timetable.html', output=to_json(output))


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, timedelta):
        serial = str(obj)
        return serial
    raise TypeError ("Type not serializable")


@timedb_blueprint.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
