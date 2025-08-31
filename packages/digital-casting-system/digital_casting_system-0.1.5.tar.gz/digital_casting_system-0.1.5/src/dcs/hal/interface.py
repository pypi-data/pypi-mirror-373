"""Device parameter interface definitions for digital casting system.

This module defines data structures and interfaces for managing device parameters
and variable definitions used in PLC communication. It provides standardized
data classes for parameter metadata, variable mapping, and machine configuration.
"""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class DeviceStruct:
  """Data structure for defining device parameter information from JSON configuration.

  This class represents a single parameter or variable definition used for
  communication between the control system and PLC. Each DeviceStruct contains
  metadata about the parameter including its identifier, variable names,
  data type, and activation status.

  Attributes:
      id (str): Unique identifier for the parameter within the device.
      var_name (str): Local variable name used in the control system.
      var_name_IN (str): PLC variable name used for actual communication.
      type (str): Data type of the parameter (BOOL, INT, REAL, STRING, etc.).
      active (bool): Whether this parameter is currently active/enabled.

  Example:
      >>> param = DeviceStruct(id="001", var_name="mixer_speed", var_name_IN="MAIN.rMixerRPM", type="REAL", active=True)
      >>> param_dict = param._to_dict()
  """

  id: str = ""
  var_name: str = ""
  var_name_IN: str = ""
  type: str = ""
  active: bool = False

  def _to_dict(self) -> dict[str, Any]:
    """Convert the DeviceStruct to a dictionary representation.

    This method converts the dataclass instance to a dictionary format
    suitable for serialization, logging, or API communication.

    Returns:
        Dict[str, Any]: Dictionary containing all parameter attributes
            with their current values.

    Example:
        >>> param = DeviceStruct(id="001", var_name="test", type="BOOL", active=True)
        >>> param_dict = param._to_dict()
        >>> print(param_dict)
        {'id': '001', 'var_name': 'test', 'var_name_IN': '', 'type': 'BOOL', 'active': True}
    """
    return dict(asdict(self).items())


@dataclass
class MixerStructOutput:
  """Data structure for mixer output parameter definitions.

  This class serves as a placeholder for mixer-specific output parameter
  structures. It can be extended to include mixer-specific output variables
  such as current mixing speed, motor status, temperature readings, etc.

  Note:
      This class is currently empty and serves as a placeholder for future
      mixer-specific output parameter implementations.

  Example:
      >>> mixer_output = MixerStructOutput()
      # Future implementation might include:
      # >>> mixer_output.current_speed = 1500  # RPM
      # >>> mixer_output.motor_temperature = 65.5  # Celsius
  """

  def __post_init__(self):
    """Placeholder for future implementation."""
    pass
