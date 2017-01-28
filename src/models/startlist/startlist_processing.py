from sqlalchemy import exc
from wtforms import Form, IntegerField, StringField, validators

from src.models.categories.categories import CategoryModel
from src.models.participants.participants import ParticipantModel
from src.models.startlist.startlist import StartlistModel


def main():
    pass


def range_generator(n):
    mylist = range(1, n + 1)
    for i in mylist:
        yield i


def process(startlist_id, category_id, startline_count):
    """Function categorizes participants based on category definition and number of starting line to
    a start list. It creates instances of a class StartlistModel, which are saved into the database

    :param start_line_count: (int) - how many people can start at the same time
    :return: writes to a database

    najdi categoriu podla ID
    ziskaj jej instaciu alebo JSON
    generuj startovaciu poziciu ludi v kategorii a uloz do databazy
    zobraz tento list na web stranke

    """
    category = CategoryModel.find_by_id(category_id)
    found_whole_category = [] # all participants in a category

    for year in range(category.year_start, category.year_end + 1):
        found = [item for item in ParticipantModel.find_by_gender_and_year(category.gender, year)]
        found_whole_category += found

    # Assignment of start start_position and start round
    start_position = range_generator(startline_count)
    start_round = 1
    for item in found_whole_category:
        try:
            start_record = StartlistModel(
                startlist_id = startlist_id,
                category_id=category.id,
                participant_id=item.id,
                start_position=next(start_position),
                start_round=start_round
            )
        except StopIteration:
            start_position = range_generator(startline_count)
            start_round += 1
            start_record = StartlistModel(
                startlist_id=startlist_id,
                category_id=category.id,
                participant_id=item.id,
                start_position=next(start_position),
                start_round=start_round
            )
        # print(start_record.json())
        start_record.save_to_db()

    return True


def get_participants():
    return ParticipantModel.list_all()


def get_categories():
    return CategoryModel.list_all()


if __name__ == "__main__":
    main()
