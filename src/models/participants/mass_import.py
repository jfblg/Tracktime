import xlrd
import csv
from os import remove
from os.path import join, abspath, dirname, isfile
from src.models.participants.participants import ParticipantModel


class MassImport:

    @staticmethod
    def insert_many(path_to_file):
        """ Insert loaded data to the db
        """

        if isfile(path_to_file):
            file_ext = MassImport.get_file_extension(path_to_file)
            print("DEBUG: ", file_ext)

            if file_ext == "xls" or file_ext == "xlsx":
                loaded_data = MassImport.read_wb(path_to_file)
            elif file_ext == "csv":
                loaded_data =  MassImport.read_csv(path_to_file)
            # This case should not happen, as MassImport.allowed_file prevents that
            else:
                return False

            for item in loaded_data:
                record = ParticipantModel(**item)
                record.save_to_db()
            remove(path_to_file)
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
            values[3] = int(values[3])
            values = dict(zip(keys, values))
            loaded_data.append(values)

        return loaded_data

    @staticmethod
    def read_csv(path_to_file):
        """Load participants from csv file"""

        keys = "first_name last_name gender year".split(" ")
        loaded_data = []

        with open(path_to_file, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                values = dict(zip(keys, row))
                print(values)
                loaded_data.append(values)

        return loaded_data

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ['csv', 'xls', 'xlsx']

    @staticmethod
    def get_file_extension(filename):
        return filename.rsplit('.', 1)[1].lower()