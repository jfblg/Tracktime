from sqlalchemy import exc
from wtforms import Form, IntegerField, StringField, validators

from src.models.categories.categories import CategoryModel
from src.models.participants.participants import ParticipantModel
from src.models.startlist.startlist import StartlistModel

LINES = 4

def main():
    pass


def process():
    # runners = ParticipantModel.find_by_gender_and_year("girl", 1997)
    # names = [runner.first_name for runner in runners]
    # print(names)


    startlist = []

    for category in get_categories():
        print(category.category_name)
        found_whole_category = []
        for year in range(category.year_start, category.year_end + 1):
            found = [item.json() for item in ParticipantModel.find_by_gender_and_year(category.gender, year)]
            found_whole_category += found

        result = {category.category_name: found_whole_category}
        startlist.append(result)

    return startlist


def get_participants():
    return ParticipantModel.list_all()


def get_categories():
    return CategoryModel.list_all()


if __name__ == "__main__":
    main()
