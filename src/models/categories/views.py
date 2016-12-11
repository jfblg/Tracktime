from flask import Blueprint, request, render_template, sessions, redirect, url_for
from src.models.categories.categories import CategoryModel, CategoryAddForm


categories_blueprint = Blueprint('categories', __name__)

@categories_blueprint.route('/list', methods=['GET'])
def list():

    data = []
    keys = "category_name year_start year_end".split(" ")
    cat1 = ["Buben1", "1996", "1996"]
    dic1 = dict(zip(keys, cat1))
    data.append(dic1)

    loaded_data = [category.json() for category in CategoryModel.list_all()]

    return render_template('categories/categories_list.html', data=loaded_data)


@categories_blueprint.route('/add', methods=['GET', 'POST'])
def add():
    form = CategoryAddForm(request.form)
    if request.method == 'POST' and form.validate():
        input_data = dict()
        input_data['category_name'] = request.form['category_name'].strip()
        input_data['gender'] = request.form['gender'].strip()
        input_data['year_start'] = request.form['year_start'].strip()
        input_data['year_end'] = request.form['year_end'].strip()

        new_category = CategoryModel(**input_data)
        new_category.save_to_db()
        return render_template('categories/categories_add_success.html', form=form, data=input_data)

    return render_template('categories/categories_add.html', form=form)