from flask import Blueprint, request, render_template, session, redirect, url_for

from src.models.timedb.timedb import TimeDbModel

timedb_blueprint = Blueprint('timedb', __name__)


@timedb_blueprint.route('/', methods=['GET', 'POST'])
def list():
    return render_template('timedb/timetable.html')