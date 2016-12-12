from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.categories.categories import CategoryModel, CategoryAddForm
from src.models.startlist.startlist import StartlistModel
from src.models.startlist.startlist_processing import *


startlist_blueprint = Blueprint('startlist', __name__)


@startlist_blueprint.route('/', methods=['GET', 'POST'])
def index():
    data = StartlistModel.join_startlist()
    return render_template('startlist/startlist.html', data=data)
