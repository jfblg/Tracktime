from sqlalchemy import exc
from wtforms import Form, IntegerField, StringField, validators

from src.models.categories.categories import CategoryModel
from src.models.participants.participants import ParticipantModel
from src.models.startlist.startlist import StartlistModel, StartlistNameModel


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

    return start_round


def process_classification(startlist_id, start_records_instances, startline_count):

    # Assignment of start start_position and start round
    start_position = range_generator(startline_count)
    start_round = 1

    for start_record_old in start_records_instances:
        try:
            start_record = StartlistModel(
                startlist_id = startlist_id,
                category_id=start_record_old.category_id,
                participant_id=start_record_old.participant_id,
                start_position=next(start_position),
                start_round=start_round
            )
        except StopIteration:
            start_position = range_generator(startline_count)
            start_round += 1
            start_record = StartlistModel(
                startlist_id=startlist_id,
                category_id=start_record_old.category_id,
                participant_id=start_record_old.participant_id,
                start_position=next(start_position),
                start_round=start_round
            )
        # print(start_record.json())
        start_record.save_to_db()

    return start_round


def result_list_generate(startlist_id):

    # Note: Not used at the moment
    # startlist_instance = StartlistNameModel.get_by_id(startlist_id)

    result_records = [result for result in StartlistModel.get_records_by_startlist_id_order_by_time(startlist_id)]

    output_list = []
    for st, pt in result_records:

        # Note: 2 decimal digits are displayed for times in results
        display_time = str(st.time_measured)[2:-4]

        # Note: Leading zeroes are stripped away
        # if display_time.startswith("00:0"):
        #     display_time = display_time[4:]
        #     print("00:0")
        # if display_time.startswith("00:"):
        #     print("00:")
        #     display_time = display_time[3:]
        # if display_time.startswith("0"):
        #     print("0")
        #     display_time = display_time[1:]

        result_item = (pt.last_name, pt.first_name, display_time)
        output_list.append(result_item)

    return output_list


def results_all():
    results = {}
    startlists_finished = [(stlist.id, stlist.name) for stlist in StartlistNameModel.list_measured_all()]
    for startlist_id, startlist_name in startlists_finished:
        results[startlist_name] = result_list_generate(startlist_id)

    return results


def get_startlist_instances():
    return [startlist_def for startlist_def in StartlistNameModel.list_all()]


def startlist_generate(startlist_id):

    records_list = []
    stlist_records = StartlistModel.get_records_by_startlist_id(startlist_id)

    for ST, PT in stlist_records:
        save_obj_tup = (PT.last_name, PT.first_name, ST.start_round, ST.start_position)
        records_list.append(save_obj_tup)

    return records_list


def get_startlist_all_frontend():

    output = {}
    startlists = get_startlist_instances()
    for item in startlists:
        output[item.name] = startlist_generate(item.id)

    return output

def get_participants():
    return ParticipantModel.list_all()


def get_categories():
    return CategoryModel.list_all()


if __name__ == "__main__":
    main()
