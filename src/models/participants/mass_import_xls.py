import xlrd
from os.path import join, abspath, dirname, isfile
from src.models.participants.participants import ParticipantModel


class MassImport:

    @staticmethod
    def insert_many(path_to_file):
        """ Insert loaded data to the db
        """

        if isfile(path_to_file):
            loaded_data = MassImport.read_wb(path_to_file)
            for item in loaded_data:
                record = ParticipantModel(**item)
                record.save_to_db()
            return True
        else:
            return False

    @staticmethod
    def read_wb(wb_path):
        """Load participants data from xls data
        """
        keys = "first_name last_name gender year".split(" ")
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
