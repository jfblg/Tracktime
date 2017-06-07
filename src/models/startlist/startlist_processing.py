import json
from pprint import pprint

from collections import namedtuple

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
        time_in_str = str(st.time_measured)
        time_format_length = len(time_in_str)
        if time_format_length == 7:
            display_time = "{}.00".format(time_in_str[2:])
        else:
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
    stlist_records = StartlistModel.get_records_by_startlist_id_order_by_round_position(startlist_id)

    for ST, PT in stlist_records:
        save_obj_tup = (ST.id, PT.last_name, PT.first_name, ST.start_round, ST.start_position)
        records_list.append(save_obj_tup)

    return records_list


def startlist_generate_length(startlist_id):
    return len(startlist_generate(startlist_id))


def startlist_get_rounds_lines(startlist_id):
    startlist_instance = StartlistNameModel.get_by_id(startlist_id).json()
    return startlist_instance['startlist_rounds'], startlist_instance['startline_count']


def update_startlist_records(startlist_id, new_data=None):
    stlist_records = [starlist_instance
                      for starlist_instance, participant_instance
                      in StartlistModel.get_records_by_startlist_id(startlist_id)]

    stlist_record_ids = [record.id for record in stlist_records]

    for new_id, new_value in new_data.items():
        changed_flag = False
        current_record = get_startlist_object_by_id(stlist_records, new_id)
        if current_record is not False:
            if int(new_id) in stlist_record_ids:
                if current_record.start_position != new_value['position']:
                    current_record.start_position = new_value['position']
                    changed_flag = True
                if current_record.start_round != new_value['round']:
                    current_record.start_round = new_value['round']
                    changed_flag = True
            if changed_flag:
                current_record.save_to_db()

    return True


def get_startlist_object_by_id(object_field, requested_id):
    for record in object_field:
        print(record.id)
        if str(record.id) == requested_id:
            return record

    return False

def parse_request_form(request_form):

    result = dict()

    for key, value in request_form.items():
        value_type, record_id = key.split("_")
        try:
            # print("A {} -> {} -> {}".format(record_id, value_type, value))
            result[record_id][value_type] = int(value)
            # print(result)

        except KeyError:
            # print("B {} -> {} -> {}".format(record_id, value_type, value))
            result[record_id] = create_empty_dict()
            result[record_id][value_type] = int(value)
            # print(result)

    return result


def create_empty_dict():
    return {"round": None, "position": None}


def wizard_input_verification(form):
    """ Verification, if the entered lines are unique. Used during time measure wizard.
    """
    # Note,that key must start with line_..., other options are ignored, to allow DNF option to work
    lines = [value for key, value in form.items() if key.startswith("line")]
    # if the entered lines are unique, they will have the same value
    if len(lines) != len(set(lines)):
        return False
    else:
        return True


def wizard_process_received_form(form):
    """ Processing of form received during the time measure
    Expected result example: {1: '00:43.42', 2: '00:41.35', 3: '00:39.14', 4: '00:27.54'}
    """
    lines = {key.split('_')[1]: value.split('_')[1] for key, value in form.items() if key.startswith("line")}
    # print(lines)
    times = {key.split('_')[1]: value for key, value in form.items() if key.startswith("time")}
    # print(times)
    return {int(value): times[key] for key, value in lines.items()}


# Note used
def startlist_to_json(startlist_id):
    ''' For editing of the start_round and start_position
    {
      "data": [
        {
          "row_id": "row_1",
          "first_name": "Tiger",
          "last_name": "Nixon",
          "start_round": "System Architect",
          "start_position": "t.nixon@datatables.net",
        },
      ]
    }
    '''
    result = dict()
    result['data'] = []
    stlist_records = StartlistModel.get_records_by_startlist_id(startlist_id)

    for ST, PT in stlist_records:
        record = dict()
        record['row_id'] = ST.id
        record['first_name'] = PT.first_name
        record['last_name'] = PT.last_name
        record['start_round'] = ST.start_round
        record['start_position'] = ST.start_position
        result['data'].append(record)

    # pprint(json.dumps(result))
    print("Loaded from AJAX")

    return json.dumps(result)



def get_startlist_all_frontend():

    # contains startlist records
    output = {}

    # contains length of the startlists - used for highlighting of a 1 athlete in a round.
    output_length = {}

    startlists = get_startlist_instances()
    for item in startlists:
        output[item.name] = startlist_generate(item.id)

    for item in startlists:
        output_length[item.name] = len(startlist_generate(item.id))

    print(output_length)

    return output, output_length

def get_participants():
    return ParticipantModel.list_all()


def get_categories():
    return CategoryModel.list_all()


if __name__ == "__main__":
    main()
