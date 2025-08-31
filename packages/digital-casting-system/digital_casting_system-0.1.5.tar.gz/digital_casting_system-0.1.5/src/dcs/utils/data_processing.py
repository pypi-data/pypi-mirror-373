import csv
import json
import os
from datetime import datetime


class DataProcessing:
  """
  This is a class that provides the data collection, processing, handlering.

  """

  def __init__(self, filename=str, data=dict):
    """Initialize the class with the filename and data."""
    # Date
    now_data = datetime.now().date().strftime("%Y%m%d")
    here = os.path.dirname(__file__)
    home = os.path.abspath(os.path.join(here, "../../../"))
    data = os.path.abspath(os.path.join(home, "data"))

    self.__date = now_data
    self.default_filename = self.__date + "_" + filename

    self.__data = data
    json_dir = os.path.join(self.__data, "json")
    csv_dir = os.path.join(self.__data, "csv")

    self.filepath_json = json_dir
    self.filepath_csv = csv_dir

    self.data = data
    self.number_recorded = 0

  @property
  def data_dict(self) -> None:
    return self.data

  @data_dict.setter
  def update_data(self, new_data) -> None:
    """ """
    self.data = new_data

  def __is_file_existed(self, filepath=str) -> bool:
    """
    check the file is aready in the folder.
    """
    if os.path.isfile(filepath):
      return True
    else:
      return False

  def write_dict_to_json(self):
    """
    write python dictionary to json format profile.

    """
    __filename = os.path.join(self.filepath_json, self.default_filename) + ".json"

    if not self.__is_file_existed(__filename):
      # Write the python dictionary to json file
      with open(__filename, "w") as f:
        json.dump(self.data, f, sort_keys=True, indent=2)
        print("\nThe json file is sucessfully exported!!!")
    else:
      self.number_recorded += 1
      __next_filename = __filename + str(self.number_recorded)

      with open(__next_filename, "w") as f:
        json.dump(self.data, f, sort_keys=True, indent=2)
        print("\nThe json file is sucessfully exported!!!")

      # raise Exception("The file is existed, PLEASE change the name")

  def write_dict_to_csv(self, header):
    """ """
    __filepath = os.path.join(self.filepath_csv, self.default_filename) + ".csv"
    # Write the python dictionary to csv file
    if not self.__is_file_existed(__filepath):
      with open(__filepath, "w+", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(self.data)
        print("\nThe csv file is sucessfully exported!!!")
    else:
      raise Exception("The file is existed, PLEASE change the name")
