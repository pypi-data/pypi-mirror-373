"""A class to load the configuration parameters via given path json."""

import json
import os


class AbbConfig:
  """AbbConfig is a class designed to load configuration parameters from a JSON file.

  This class loads configuration parameters from a JSON file located in the project's
  config directory. It provides timeout settings for robot controller communication.

  Attributes:
      TIMEOUT (int): Timeout in seconds to avoid freezing the main thread if the
          controller is unavailable.
      TIMEOUT_LONG (int): Extended timeout in seconds for time-consuming processes
          such as slow motions.
  """

  def __init__(self):
    """Initialize the ABB configuration by loading parameters from a JSON file.

    Sets the following attributes based on the configuration file:
    - TIMEOUT: Standard timeout for robot communication
    - TIMEOUT_LONG: Extended timeout for slow operations

    Raises:
        KeyError: If required configuration keys are missing in the JSON file.
        ValueError: If the configuration values cannot be converted to integers.
        FileNotFoundError: If the configuration file cannot be found.
        json.JSONDecodeError: If the JSON file is malformed.
    """
    config = self._load_from_json()
    self.TIMEOUT = int(config["TIMEOUT"])
    self.TIMEOUT_LONG = int(config["TIMEOUT_LONG"])

  def _load_from_json(self) -> dict:
    """Load configuration parameters from JSON file.

    Loads the setup.json configuration file from the config directory
    relative to this module's location.

    Returns:
        dict: Configuration parameters loaded from JSON file. Returns empty
            dict if file cannot be read or parsed.

    Note:
        Prints error message to console if JSON parsing fails, but does not
        raise an exception to allow graceful degradation.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dir_path, "..", "config", "setup.json")
    with open(filename) as f:
      try:
        output = json.load(f)
      except ValueError as e:
        print(f"Error reading the JSON file: {e}")
        output = {}
    return output
