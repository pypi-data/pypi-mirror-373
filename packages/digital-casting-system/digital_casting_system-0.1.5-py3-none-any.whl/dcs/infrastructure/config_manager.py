"""Configuration manager for project and machine settings.

This module provides centralized configuration management for the digital casting
system, handling robot configurations, PLC settings, and other system parameters
loaded from JSON configuration files with structured data objects.
"""

import json
import os
from typing import Any

from ..data.struct import DataObject, DataParam


class ConfigManager:
  """Manages configuration for project and machine settings.

  The ConfigManager provides a centralized interface for loading and accessing
  configuration data for various components of the digital casting system,
  including robot controllers, PLC settings, and machine parameters.

  Configuration files are loaded and converted to structured data objects,
  with all machine parameters kept in memory for efficient access by HAL classes.

  Attributes:
      _HERE (str): Directory path of this module file.
      _HOME (str): Root directory path of the project.
      _config_dir (str): Directory path where configuration files are stored.
      machines (Dict[str, DataParam]): In-memory storage of machine configurations.

  Example:
      >>> config = ConfigManager()
      >>> config.load_plc_config()
      >>> inline_mixer = config.get_machine("inline_mixer")
      >>> print(f"Machine ID: {inline_mixer.machine_id}")
  """

  def __init__(self) -> None:
    """Initialize configuration manager with default paths.

    Sets up the directory paths used for locating configuration files
    relative to the current module location and initializes machine storage.
    """
    self._HERE = os.path.dirname(__file__)
    self._HOME = os.path.abspath(os.path.join(self._HERE, "../../"))
    self._config_dir = os.path.abspath(os.path.join(self._HERE, "../_config"))
    self.machines: dict[str, DataParam] = {}

  def get_robot_config(self, filepath: str | None = None) -> dict[str, Any]:
    """Get robot configuration from JSON file.

    Loads and returns the ABB IRB4600 robot configuration including
    communication settings, coordinate systems, tool definitions,
    and operational parameters.

    Args:
        filepath (str, optional): Custom path to robot config file.

    Returns:
        Dict[str, Any]: Dictionary containing robot configuration data
            including network settings, coordinate frames, joint limits,
            and other robot-specific parameters.

    Raises:
        FileNotFoundError: If the robot configuration file is not found.
        ValueError: If the configuration file contains invalid JSON.

    Example:
        >>> config = ConfigManager()
        >>> robot_config = config.get_robot_config()
        >>> ip_address = robot_config.get("network", {}).get("ip")
        >>> joint_limits = robot_config.get("joint_limits", [])
    """
    config_path = filepath or os.path.join(self._config_dir, "abb_irb4600.json")
    return self._load_json_config(config_path)

  def get_plc_config(self, filepath: str | None = None) -> dict[str, Any]:
    """Get PLC configuration from JSON file as raw dictionary.

    Loads and returns the Beckhoff TwinCAT PLC configuration as a dictionary.
    For structured data access, use load_plc_config() followed by get_machine().

    Args:
        filepath (str, optional): Custom path to PLC config file.

    Returns:
        Dict[str, Any]: Dictionary containing PLC configuration data
            including ADS settings, network parameters, variable lists,
            and machine definitions.

    Raises:
        FileNotFoundError: If the PLC configuration file is not found.
        ValueError: If the configuration file contains invalid JSON.

    Example:
        >>> config = ConfigManager()
        >>> plc_config = config.get_plc_config()
        >>> netid = plc_config.get("network", {}).get("netid")
        >>> machines = plc_config.get("machines", [])
    """
    config_path = filepath or os.path.join(self._config_dir, "beckhoff_controller.json")
    return self._load_json_config(config_path)

  def load_plc_config(self, filepath: str | None = None) -> None:
    """Load PLC configuration and convert to structured data objects.

    Loads the PLC configuration file and converts all machine definitions
    to DataParam objects, storing them in memory for efficient access.
    This method should be called before using get_machine().

    Args:
        filepath (str, optional): Custom path to PLC config file.

    Raises:
        FileNotFoundError: If the PLC configuration file is not found.
        ValueError: If the configuration file contains invalid JSON.

    Example:
        >>> config = ConfigManager()
        >>> config.load_plc_config()
        >>> inline_mixer = config.get_machine("inline_mixer")
    """
    config_path = filepath or os.path.join(self._config_dir, "beckhoff_controller.json")
    raw_config = self._load_json_config(config_path)

    # Convert raw config to structured data objects
    for machine_name, machine_data in raw_config.items():
      self.machines[machine_name] = self._convert_to_data_param(machine_data)

  def get_machine(self, machine_name: str) -> DataParam:
    """Get a specific machine configuration as structured data.

    Retrieves a machine configuration that was previously loaded using
    load_plc_config(). The machine data includes structured input and
    output variable definitions.

    Args:
        machine_name (str): Name of the machine to retrieve.

    Returns:
        DataParam: Structured machine configuration with input/output variables.

    Raises:
        KeyError: If the machine name is not found in loaded configurations.
        RuntimeError: If load_plc_config() has not been called first.

    Example:
        >>> config = ConfigManager()
        >>> config.load_plc_config()
        >>> inline_mixer = config.get_machine("inline_mixer")
        >>> print(f"Machine ID: {inline_mixer.machine_id}")
        >>> for output_var in inline_mixer.machine_output:
        ...   print(f"Output: {output_var.var_name}")
    """
    if not self.machines:
      raise RuntimeError("No machines loaded. Call load_plc_config() first.")

    if machine_name not in self.machines:
      available_machines = list(self.machines.keys())
      raise KeyError(f"Machine '{machine_name}' not found. Available machines: {available_machines}")

    return self.machines[machine_name]

  def get_all_machines(self) -> dict[str, DataParam]:
    """Get all loaded machine configurations.

    Returns a dictionary of all machine configurations that were loaded
    using load_plc_config().

    Returns:
        Dict[str, DataParam]: Dictionary mapping machine names to their configurations.

    Raises:
        RuntimeError: If load_plc_config() has not been called first.

    Example:
        >>> config = ConfigManager()
        >>> config.load_plc_config()
        >>> all_machines = config.get_all_machines()
        >>> for name, machine in all_machines.items():
        ...   print(f"Machine: {name}, ID: {machine.machine_id}")
    """
    if not self.machines:
      raise RuntimeError("No machines loaded. Call load_plc_config() first.")

    return self.machines.copy()

  def _convert_to_data_param(self, machine_data: dict) -> DataParam:
    """Convert raw machine configuration to DataParam object.

    Internal method to convert dictionary-based machine configuration
    to structured DataParam objects with DataObject variables.

    Args:
        machine_data (dict): Raw machine configuration from JSON.

    Returns:
        DataParam: Structured machine configuration object.
    """
    machine_id = int(machine_data["machine_id"])

    # Convert input variables
    inputs = []
    for input_data in machine_data.get("input", []):
      inputs.append(
        DataObject(
          id=int(input_data["id"]),
          var_name=input_data["var_name"],
          var_name_IN=input_data["var_name_IN"],
          data_type=input_data["data_type"],
          active=input_data["active"],
        )
      )

    # Convert output variables
    outputs = []
    for output_data in machine_data.get("output", []):
      outputs.append(
        DataObject(
          id=int(output_data["id"]),
          var_name=output_data["var_name"],
          var_name_IN=output_data["var_name_IN"],
          data_type=output_data["data_type"],
          active=output_data["active"],
        )
      )

    return DataParam(machine_id, inputs, outputs)

  def _load_json_config(self, config_path: str) -> dict[str, Any]:
    """Load configuration from JSON file.

    Internal method for loading and parsing JSON configuration files
    with proper error handling for missing files and invalid JSON.

    Args:
        config_path (str): Full path to the JSON configuration file.

    Returns:
        Dict[str, Any]: Parsed JSON data as a dictionary.

    Raises:
        FileNotFoundError: If configuration file is not found.
        ValueError: If configuration file contains invalid JSON.
    """
    try:
      with open(config_path) as f:
        return json.load(f)
    except FileNotFoundError:
      raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
      raise ValueError(f"Invalid JSON in configuration file: {config_path}")
