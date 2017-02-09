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
    output = [(item.id, str(item.time_measured)[:-4], item.order_number) for item in TimeDbModel.list_all()]
    # output = [item.json() for item in TimeDbModel.list_all()]
    position = request.form.get('position',0, type=int)
    print(position)
    output = output[-position:]
    print(output)

    # print(request.form['username'])
    # return jsonify(result=result)
    return render_template('timedb/timetable.html', data=output)
    # return "abc"
    # # return jsonify(result=output)