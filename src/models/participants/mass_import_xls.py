import xlrd
import pprint
from os.path import join, abspath, dirname

from src.models.participants.participants import ParticipantModel

WB = "registered.xlsx"

def main():
   loaded_data = read_wb(WB)



def insert_many():
    """ Insert loaded data to the db

    :return:
    """
    loaded_data = read_wb(xls_path())

    for item in loaded_data:
        record = ParticipantModel(**item)
        record.save_to_db()
        # print(record.json())


def xls_path():
    app_root_folder = dirname(dirname(dirname(dirname(abspath(__file__)))))
    return join(app_root_folder, 'sample_data', WB)


def read_wb(wb_path):
    """Load participants data from xls data
    """
    keys = "first_name last_name year gender email_addr".split(" ")
    loaded_data = []

    xl_workbook = xlrd.open_workbook(wb_path)
    xl_sheet = xl_workbook.sheet_by_index(0)


    for row_idx in range(1, xl_sheet.nrows):
        values = [item.value for item in xl_sheet.row(row_idx)]
        # converting year from float to int
        values[2] = int(values[2])
        values = dict(zip(keys, values))
        loaded_data.append(values)

    return loaded_data


if __name__ == "__main__":
    main()
