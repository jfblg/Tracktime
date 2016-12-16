from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.categories.categories import CategoryModel, CategoryAddForm
from src.models.startlist.startlist import StartlistModel
from src.models.startlist.startlist_processing import *

import pprint

startlist_blueprint = Blueprint('startlist', __name__)


@startlist_blueprint.route('/', methods=['GET', 'POST'])
def index():
    output = []

    categories = [(cat_id, cat_name) for cat_id, cat_name in CategoryModel.list_categories_ordered()]

    for cat_id, cat_name in categories:
        output_emb = []
        output_emb.append(cat_name)

        cat_participants_names = [(start_table, part_table) for start_table, part_table in StartlistModel.get_startlist_by_category_with_names(cat_id)]
        output_emb.append(cat_participants_names)

        output.append(output_emb)

    return render_template('startlist/startlist.html', data=output)
