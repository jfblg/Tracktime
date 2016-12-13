from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.categories.categories import CategoryModel, CategoryAddForm
from src.models.startlist.startlist import StartlistModel
from src.models.startlist.startlist_processing import *

import pprint

startlist_blueprint = Blueprint('startlist', __name__)


@startlist_blueprint.route('/', methods=['GET', 'POST'])
def index():

    cli = StartlistModel.join_experiment(4)
    print(cli)

    # data = [item for item in StartlistModel.join_startlist()]
    output = {}
    categories = [item for item in CategoryModel.list_all()]
    for category in categories:
        output[category.category_name] = [item for item in StartlistModel.join_startlist(category.id)]

    pprint.pprint(output)
    return render_template('startlist/startlist.html', data=output)
