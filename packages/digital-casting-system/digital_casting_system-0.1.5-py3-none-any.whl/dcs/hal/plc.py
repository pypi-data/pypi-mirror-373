"""PLC hardware abstraction layer module.

This module provides a hardware abstraction class for reading and writing variables
from and to Beckhoff TwinCAT PLC controllers using the pyads library.
"""

from itertools import chain
from threading import Lock
from typing import Any

import pyads
from attr import define, field, validators


@define
class PLC:
  """Hardware abstraction class for reading and writing variables from and to PLC.

  This class provides thread-safe communication with Beckhoff TwinCAT PLC controllers
  using the ADS (Automation Device Specification) protocol. It manages connection
  state, variable lists, and provides methods for reading and writing PLC variables.

  Attributes:
      netid (str): Network ID of the PLC controller (format: "x.x.x.x.x.x")
      ip (str): IP address of the PLC controller
      plc_vars_input (list): List of input variables that can be written to the PLC
      plc_vars_output (list): List of output variables that can be read from the PLC
      connection (pyads.Connection): ADS connection object to the PLC
      lock_dict (Lock): Thread lock for dictionary operations
      lock_ads (Lock): Thread lock for ADS communication operations

  Example:
      >>> plc = PLC(netid="192.168.1.100.1.1", ip="192.168.1.100")
      >>> if plc.connect():
      ...   value = plc.get_variable("MAIN.bStartButton")
      ...   plc.set_variable("MAIN.bLED", True)
      ...   plc.close()
  """

  netid: str = field(validator=validators.instance_of(str))
  """Network ID of the PLC controller in ADS format."""

  ip: str
  """IP address of the PLC controller."""

  plc_vars_input: list[Any] = field(factory=list)
  """List of input variables that can be written to the PLC."""

  plc_vars_output: list[Any] = field(factory=list)
  """List of output variables that can be read from the PLC."""

  connection: Any = field(default=None)
  """ADS connection object to the PLC."""

  lock_dict: Lock = field(factory=Lock)
  """Thread lock for protecting dictionary operations."""

  lock_ads: Lock = field(factory=Lock)
  """Thread lock for protecting ADS communication operations."""

  def __attrs_post_init__(self) -> None:
    """Initialize the ADS connection object after instance creation.

    This method is automatically called after the instance is created
    and sets up the pyads connection with the specified netid and PLC port.
    """
    self.connection = pyads.Connection(self.netid, pyads.PORT_TC3PLC1)

  def close(self) -> None:
    """Close the connection to the PLC.

    This method closes the active ADS connection to the PLC if it's currently open.
    It's important to call this method to properly release network resources
    when communication with the PLC is no longer needed.

    Note:
        This method will print a confirmation message when the connection is closed.
    """
    if self.connection.is_open:
      self.connection.close()
    print("PLC connection closed")

  def connect(self) -> bool:
    """Establish connection to the PLC.

    This method attempts to open an ADS connection to the PLC and verifies
    the connection by reading device information. The connection attempt is
    thread-safe using the ADS lock.

    Returns:
        bool: True if connection was successful, False otherwise.

    Note:
        Connection status and any errors are printed to the console.
        Multiple calls to this method are safe - it will only open the
        connection if it's not already open.

    Example:
        >>> plc = PLC(netid="192.168.1.100.1.1", ip="192.168.1.100")
        >>> if plc.connect():
        ...   print("Successfully connected to PLC")
        ... else:
        ...   print("Failed to connect to PLC")
    """
    with self.lock_ads:
      if not self.connection.is_open:
        self.connection.open()
      try:
        self.connection.read_device_info()
      except pyads.ADSError as e:
        print(f"Error: {e}")
        return False
      else:
        print(f"Connection: {self.connection.is_open}")
        return True

  def set_plc_vars_input_list(self, plc_vars_input: list[Any]) -> None:
    """Load input variables list from the PLC configuration.

    This method sets or extends the list of input variables that can be
    written to the PLC. Input variables are typically setpoints, commands,
    or configuration parameters sent from the control system to the PLC.

    Args:
        plc_vars_input (List[Any]): List of input variable objects containing
            variable definitions, names, data types, and other metadata.

    Note:
        If the input list is empty, it will be replaced with the new list.
        If the input list already contains variables, the new variables
        will be appended to the existing list.

    Example:
        >>> vars = [{"name": "MAIN.rSetTemp", "type": "REAL"}, {"name": "MAIN.bStart", "type": "BOOL"}]
        >>> plc.set_plc_vars_input_list(vars)
    """
    if not self.plc_vars_input:
      self.plc_vars_input = [vars for vars in plc_vars_input]
    else:
      self.plc_vars_input.extend([vars for vars in plc_vars_input])

  def set_plc_vars_output_list(self, plc_vars_output: list[Any]) -> None:
    """Load output variables list from the PLC configuration.

    This method sets or extends the list of output variables that can be
    read from the PLC. Output variables are typically sensor values, status
    information, or feedback data sent from the PLC to the control system.

    Args:
        plc_vars_output (List[Any]): List of output variable objects containing
            variable definitions, names, data types, and other metadata.

    Note:
        If the output list is empty, it will be replaced with the new list.
        If the output list already contains variables, the new variables
        will be appended to the existing list.

    Example:
        >>> vars = [{"name": "MAIN.rCurrTemp", "type": "REAL"}, {"name": "MAIN.bRunning", "type": "BOOL"}]
        >>> plc.set_plc_vars_output_list(vars)
    """
    if not self.plc_vars_output:
      self.plc_vars_output = [vars for vars in plc_vars_output]
    else:
      self.plc_vars_output.extend([vars for vars in plc_vars_output])

  def read_variables(self) -> None:
    """Read all configured variables from the PLC and store them internally.

    This method reads all variables from the configured output variable list
    and stores their values for later retrieval. The operation is thread-safe
    and requires an active PLC connection.

    Raises:
        AdsConnectionError: If the PLC connection cannot be established.
        NotImplementedError: This method is not yet fully implemented.

    Note:
        This method is currently a placeholder and raises NotImplementedError.
        Full implementation would batch-read all configured variables for
        improved performance.

    Example:
        >>> plc.connect()
        >>> plc.read_variables()  # Reads all configured variables
    """
    if not self.connect():
      raise AdsConnectionError("Could not read variable from PLC, PLC connection failed.")
    with self.lock_ads:
      raise NotImplementedError

  def write_variables(self) -> None:
    """Write all modified variables to the PLC.

    This method writes all variables that have been modified or queued for
    writing to the PLC. The operation is thread-safe and requires an active
    PLC connection.

    Raises:
        AdsConnectionError: If the PLC connection cannot be established.
        NotImplementedError: This method is not yet fully implemented.

    Note:
        This method is currently a placeholder and raises NotImplementedError.
        Full implementation would batch-write all modified variables for
        improved performance.

    Example:
        >>> plc.connect()
        >>> plc.write_variables()  # Writes all modified variables
    """
    if not self.connect():
      raise AdsConnectionError("Could not read variable from PLC, PLC connection failed.")
    with self.lock_ads:
      raise NotImplementedError

  def check_variables_active(self) -> None:
    """Check which variables are currently active and available.

    This method verifies the availability and status of all configured
    variables in the PLC. It can be used to validate configuration and
    ensure that all required variables are accessible.

    Raises:
        NotImplementedError: This method is not yet implemented.

    Note:
        This method is currently a placeholder and raises NotImplementedError.
        Full implementation would check variable accessibility and status.
    """
    raise NotImplementedError

  def get_variable(self, variable_name: str) -> Any:
    """Read a specific variable value from the PLC.

    This method reads the current value of a single variable from the PLC.
    The variable must be present in either the input or output variable lists
    and must be marked as active.

    Args:
        variable_name (str): Name of the variable to read from the PLC.
            Must match the var_name_IN field of a configured variable.

    Returns:
        Any: The current value of the variable as read from the PLC.
            The type depends on the variable's data type (BOOL, INT, REAL, etc.).

    Raises:
        VariableNotFoundInRepositoryError: If the variable is not found in the
            configured variable lists or is marked as inactive.

    Note:
        This method is thread-safe and searches through both input and output
        variable lists. The variable must be marked as active (active != "false").

    Example:
        >>> plc = PLC(netid="192.168.1.100.1.1", ip="192.168.1.100")
        >>> plc.connect()
        >>> temperature = plc.get_variable("MAIN.rCurrentTemperature")
        >>> print(f"Current temperature: {temperature}°C")
    """
    with self.lock_dict:
      for data in chain(self.plc_vars_output, self.plc_vars_input):
        if data.active != "false" and variable_name == str(data.var_name_IN):
          try:
            value = self.connection.read_by_name(data.var_name_IN)
            print(f"Variable {variable_name}:{value} read from plc.")
            return value
          except KeyError:
            error_msg = f"Error{variable_name}, Error number: {data.id}"
            raise VariableNotFoundInRepositoryError(error_msg)

  def set_variable(self, variable_name: str, value: Any) -> Any:
    """Write a specific variable value to the PLC.

    This method writes a value to a single variable in the PLC. The variable
    must be present in the input variable list and must be marked as active.

    Args:
        variable_name (str): Name of the variable to write to the PLC.
            Must match the var_name field of a configured input variable.
        value (Any): The value to write to the variable. The type should
            match the variable's data type (BOOL, INT, REAL, etc.).

    Returns:
        Any: The result of the write operation (typically None for successful writes).

    Raises:
        VariableNotFoundInRepositoryError: If the variable is not found in the
            configured input variable list or is marked as inactive.

    Note:
        This method is thread-safe and only searches through input variable
        lists since output variables are read-only from the control system perspective.
        The variable must be marked as active (active != "false").

    Example:
        >>> plc = PLC(netid="192.168.1.100.1.1", ip="192.168.1.100")
        >>> plc.connect()
        >>> plc.set_variable("MAIN.bStartProcess", True)
        >>> plc.set_variable("MAIN.rSetTemperature", 25.5)
    """
    with self.lock_dict:
      for data in self.plc_vars_input:
        if data.active != "false" and variable_name == str(data.var_name):
          try:
            value = self.connection.write_by_name(data.var_name_IN, value)
            print(f"Variable {variable_name}:{value} write to plc.")
            return value
          except KeyError:
            error_msg = f"Error{variable_name}, Error number: {data.id}"
            raise VariableNotFoundInRepositoryError(error_msg)


class LocalRepositoryEmptyError(Exception):
  """Exception raised when the local variable repository is empty.

  This exception is raised when attempting to perform operations that require
  configured variables, but no variables have been loaded into the PLC instance.

  Attributes:
      message (str): Explanation of the error.
  """

  pass


class VariableNotFoundInRepositoryError(Exception):
  """Exception raised when a requested variable is not found in the repository.

  This exception is raised when attempting to read or write a variable that
  is not present in the configured variable lists, or when the variable is
  marked as inactive.

  Attributes:
      message (str): Explanation of the error including variable name and ID.
  """

  pass


class AdsConnectionError(Exception):
  """Exception raised when ADS connection to the PLC fails.

  This exception is raised when the PLC connection cannot be established
  or when communication errors occur during variable read/write operations.

  Attributes:
      message (str): Explanation of the connection error.
  """

  pass
