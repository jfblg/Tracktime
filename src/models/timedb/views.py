from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify

from src.models.timedb.timedb import TimeDbModel

timedb_blueprint = Blueprint('timedb', __name__)


@timedb_blueprint.route('/', methods=['GET', 'POST'])
def list():


    output = [(item.id, item.time_measured, item.order_number) for item in TimeDbModel.list_all()]
    position = 4

    if request.method == 'POST':
        requested = request.form['position']
        position = int(requested)
        print(position)
        print(type(position))

    output = output[-position:]
    # print(output)
    return render_template('timedb/timetable.html', data=output)


@timedb_blueprint.route('/_last_x_times', methods=['POST'])
def get_last_x():
    # output = [(item.id, item.time_measured, item.order_number) for item in TimeDbModel.list_all()]
    # position = int(request.form['position'])
    # output = output[-position:]
    # return render_template('timedb/timetable.html', data=output)
    a = request.form.get('a', 1, type=int)
    b = request.form.get('b', 0, type=int)
    print(request.form['username'])
    return jsonify(result=a + b)
    # return jsonify(result=output)