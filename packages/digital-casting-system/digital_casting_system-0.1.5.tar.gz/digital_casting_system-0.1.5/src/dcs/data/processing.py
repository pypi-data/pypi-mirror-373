import csv
import json
import os

from .struct import DataObject, DataParam


class DataGathering:
  """
  A class to handle data gathering from the PLC and export to files.

  This class provides functionality for collecting data during PLC operations
  and exporting it to JSON and CSV formats for analysis and storage.

  Attributes:
      _DATA (str): The absolute path of the data directory.
      _JSON_DIR (str): The absolute path of the json directory.
      _CSV_DIR (str): The absolute path of the csv directory.
      filename (str): Base filename for data export files.

  Example:
      >>> gatherer = DataGathering("experiment_01")
      >>> data = {"timestamp": "2024-01-01", "value": 42.5}
      >>> gatherer.write_dict_to_json(data)
      >>> gatherer.write_dict_to_csv([data], ["timestamp", "value"])
  """

  def __init__(self, filename: str) -> None:
    """Initialize data gathering with specified filename.

    Args:
        filename (str): Base filename for exported data files.
    """
    self._HERE = os.path.dirname(__file__)
    self._HOME = os.path.abspath(os.path.join(self._HERE, "../../../"))
    self._DATA = os.path.abspath(os.path.join(self._HOME, "data"))
    self._JSON_DIR = os.path.join(self._DATA, "json")
    self._CSV_DIR = os.path.join(self._DATA, "csv")
    self.filename = filename

  def write_dict_to_json(self, data: dict) -> None:
    """Export dictionary data to JSON file.

    Writes the provided dictionary to a JSON file in the configured
    JSON directory with the specified filename.

    Args:
        data (dict): Data dictionary to export to JSON.

    Example:
        >>> gatherer = DataGathering("test_data")
        >>> data = {"sensor_1": 25.3, "sensor_2": 42.1}
        >>> gatherer.write_dict_to_json(data)
    """
    path = os.path.join(self._JSON_DIR, self.filename) + ".json"
    # Write the python dictionary to json file
    with open(path, "w") as f:
      json.dump(data, f, sort_keys=True, indent=5)
      print(f"\nThe json file is sucessfully exported! in {path}")

  def write_dict_to_csv(self, data: list, header: list) -> None:
    """Export list of dictionaries to CSV file.

    Writes the provided data list to a CSV file in the configured
    CSV directory with the specified filename and header.

    Args:
        data (list): List of dictionaries containing row data.
        header (list): List of column headers for the CSV file.

    Example:
        >>> gatherer = DataGathering("sensor_log")
        >>> data = [{"time": "10:00", "temp": 25.3}, {"time": "10:01", "temp": 25.5}]
        >>> header = ["time", "temp"]
        >>> gatherer.write_dict_to_csv(data, header)
    """
    path = os.path.join(self._CSV_DIR, self.filename) + ".csv"
    # Write the python dictionary to csv file
    with open(path, "w+", newline="") as f:
      writer = csv.DictWriter(f, fieldnames=header)
      writer.writeheader()
      writer.writerows(data)
      print(f"\nThe csv file is sucessfully exported! in {self._CSV_DIR}")


# Legacy compatibility - DataHandler class for backwards compatibility
class DataHandler:
  """Legacy DataHandler class - DEPRECATED.

  This class is maintained for backwards compatibility but should not be used
  in new code. Use ConfigManager from dcs.infrastructure.config_manager instead.

  Example:
      >>> # OLD (deprecated):
      >>> from dcs.data.processing import DataHandler
      >>> handler = DataHandler()
      >>> # NEW (recommended):
      >>> from dcs.infrastructure.config_manager import ConfigManager
      >>> config = ConfigManager()
      >>> config.load_plc_config()
  """

  def __init__(self) -> None:
    """Initialize legacy DataHandler."""
    import warnings

    warnings.warn(
      "DataHandler is deprecated. Use ConfigManager from dcs.infrastructure.config_manager instead.",
      DeprecationWarning,
      stacklevel=2,
    )

    self._HERE = os.path.dirname(__file__)
    self._HOME = os.path.abspath(os.path.join(self._HERE, "../../../"))
    self._config = os.path.abspath(os.path.join(self._HERE, "..", "_config"))
    self.filename = ""
    self.machine_dict = dict()
    self.machine_id = 0
    self.machine_input = []
    self.machine_output = []
    self.machine = DataParam(self.machine_id, self.machine_input, self.machine_output)

  def _set_plc_mode_config(self) -> None:
    """Set PLC configuration file path."""
    self.filename = os.path.join(self._config, "beckhoff_controller.json")

  def _set_robot_mode_config(self) -> None:
    """Set robot configuration file path."""
    self.filename = os.path.join(self._config, "abb_irb4600.json")

  def _load_json_to_instance(self) -> None:
    """Load JSON configuration to instance."""
    with open(self.filename) as file:
      try:
        self.machine = json.load(file, object_hook=self.data_object_decoder)
      except ValueError as e:
        print(f"Error: {e}")

  @staticmethod
  def data_object_decoder(obj) -> object:
    """Decode JSON object to DataParam."""
    if "machine_id" in obj:
      machine_id = obj["machine_id"]
      inputs = [DataObject(**input_data) for input_data in obj.get("input", [])]
      outputs = [DataObject(**output_data) for output_data in obj.get("output", [])]
      return DataParam(machine_id, inputs, outputs)
    return obj

  def __str__(self) -> str:
    """String representation of DataHandler."""
    return str(f"Here: {self._HERE} \nHome: {self._HOME} \nConfig: {self._config}")
