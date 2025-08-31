"""Device abstraction layer for digital casting system machines.

This module defines the abstract Machine interface and concrete implementations
for various digital casting system devices including inline mixers, concrete pumps,
and dosing pumps. Each machine class provides standardized interfaces for
accessing device parameters, input/output variables, and communication settings.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


class Machine(ABC):
  """Abstract base class for digital casting system machines.

  This abstract class defines the interface that all machine implementations
  must follow. It provides standard methods for accessing device information,
  parameter lists, and variable configurations needed for PLC communication.

  All concrete machine classes must implement the abstract methods to provide
  device-specific functionality while maintaining a consistent interface.
  """

  @abstractmethod
  def device_id(self) -> int:
    """Get the unique device identifier for this machine.

    Returns:
        int: Unique identifier for the device, used for communication routing
            and device management within the digital casting system.
    """
    raise NotImplementedError

  @abstractmethod
  def parameter_id(self, param_name: str) -> int:
    """Get the parameter ID for a specific parameter name.

    Args:
        param_name (str): Name of the parameter to look up.

    Returns:
        int: Unique identifier for the specified parameter, or 0 if not found.
    """
    raise NotImplementedError

  @abstractmethod
  def input_list(self) -> list[object]:
    """Get the list of input parameters for this machine.

    Returns:
        List[object]: List of input parameter objects that can be written to
            the machine for control and configuration purposes.
    """
    raise NotImplementedError

  @abstractmethod
  def output_list(self) -> list[object]:
    """Get the list of output parameters for this machine.

    Returns:
        List[object]: List of output parameter objects that can be read from
            the machine for status monitoring and feedback.
    """
    raise NotImplementedError

  @abstractmethod
  def get_input_var_name(self) -> Iterator[Any]:
    """Get an iterator of input variable names.

    Yields:
        Any: Variable names for all input parameters of this machine.
    """
    raise NotImplementedError

  @abstractmethod
  def get_output_var_name(self) -> Iterator[Any]:
    """Get an iterator of output variable names.

    Yields:
        Any: Variable names for all output parameters of this machine.
    """
    raise NotImplementedError

  @abstractmethod
  def set_input_dict(self) -> Iterator[dict]:
    """Generate input variable dictionary for PLC communication.

    Yields:
        dict: Dictionary entries containing variable name mappings and
            data type information for active input variables.
    """
    raise NotImplementedError

  @abstractmethod
  def set_output_dict(self) -> Iterator[dict]:
    """Generate output variable dictionary for PLC communication.

    Yields:
        dict: Dictionary entries containing variable name mappings and
            data type information for active output variables.
    """
    raise NotImplementedError


@dataclass
class InlineMixer(Machine):
  """Inline mixer machine implementation for concrete mixing operations.

  The InlineMixer class represents an inline concrete mixing device that blends
  cement, water, and additives in a continuous process. This machine provides
  real-time control of mixing parameters and monitoring of process variables.

  Attributes:
      machine_id (int): Unique identifier for this mixer instance.
      machine_input (List[object]): List of input parameter objects for mixer control.
      machine_output (List[object]): List of output parameter objects for mixer monitoring.
      machine_error_num (int): Current error count or error state indicator (default: 0).

  Example:
      >>> mixer_inputs = [param1, param2, param3]  # Parameter objects
      >>> mixer_outputs = [status1, status2]  # Status objects
      >>> mixer = InlineMixer(machine_id=1, machine_input=mixer_inputs, machine_output=mixer_outputs)
      >>> print(f"Mixer ID: {mixer.device_id()}")
  """

  machine_id: int
  machine_input: list[object]
  machine_output: list[object]
  machine_error_num: int = 0

  def device_id(self) -> int:
    """Get the unique device identifier for this mixer.

    Returns:
        int: The machine_id assigned to this inline mixer instance.
    """
    return self.machine_id

  def parameter_id(self, param_name: str) -> int:
    """Get the parameter ID for a specific parameter name.

    Searches through both input and output parameter lists to find
    a parameter with the specified name and returns its ID.

    Args:
        param_name (str): Name of the parameter to look up.

    Returns:
        int: Parameter ID if found, 0 if parameter not found or has no ID.
    """
    for params in [self.machine_input, self.machine_output]:
      for param in params:
        if param_name == param.var_name:
          return param.id if param.id is not None else 0
    return 0

  def input_list(self) -> list[object]:
    """Get the list of input parameters for mixer control.

    Returns:
        List[object]: List of input parameter objects that can be used
            to control mixer operation (flow rates, mixing speeds, etc.).
    """
    return self.machine_input

  def output_list(self) -> list[object]:
    """Get the list of output parameters for mixer monitoring.

    Returns:
        List[object]: List of output parameter objects that provide
            mixer status and measurement data.
    """
    return self.machine_output

  def get_input_var_name(self) -> Iterator[Any]:
    """Get an iterator of input variable names.

    Yields:
        Any: Variable name for each input parameter of this mixer.
    """
    for input_param in self.machine_input:
      yield input_param.var_name

  def get_output_var_name(self) -> Iterator[Any]:
    """Get an iterator of output variable names.

    Yields:
        Any: Variable name for each output parameter of this mixer.
    """
    for output_param in self.machine_output:
      yield output_param.var_name

  def set_input_dict(self) -> Iterator[dict]:
    """Generate input variable dictionary for PLC communication.

    Creates dictionary entries for active input variables with their
    PLC variable names, data types, and configuration flags.

    Yields:
        dict: Dictionary with variable name as key and list containing
            PLC variable name, pyads data type, and flag as value.
            Format: {var_name: [var_name_IN, "pyads.DATA_TYPE", 1]}
    """
    for input_param in self.machine_input:
      if input_param.active:
        yield {input_param.var_name: [input_param.var_name_IN, "pyads." + input_param.data_type, 1]}

  def set_output_dict(self) -> Iterator[dict]:
    """Generate output variable dictionary for PLC communication.

    Creates dictionary entries for active output variables with their
    PLC variable names, data types, and configuration flags.

    Yields:
        dict: Dictionary with variable name as key and list containing
            PLC variable name, pyads data type, and flag as value.
            Format: {var_name: [var_name_IN, "pyads.DATA_TYPE", 1]}
    """
    for output_param in self.machine_output:
      if output_param.active:
        yield {output_param.var_name: [output_param.var_name_IN, "pyads." + output_param.data_type, 1]}

  def __str__(self) -> str:
    """String representation of the inline mixer.

    Returns:
        str: Human-readable string describing the mixer configuration.
    """
    return f"Machine ID: {self.machine_id}, Machine Input: {self.input_list}, Machine Output: {self.output_list}"


@dataclass
class ConcretePump(Machine):
  """Concrete pump machine implementation for material transport operations.

  The ConcretePump class represents a concrete pumping device that transports
  mixed concrete from the mixer to the casting location. This machine provides
  control of pumping parameters and monitoring of system status.

  Attributes:
      machine_id (int): Unique identifier for this pump instance.
      machine_input (List[object]): List of input parameter objects for pump control.
      machine_output (List[object]): List of output parameter objects for pump monitoring.
      machine_error_num (int): Current error count or error state indicator (default: 0).
  """

  machine_id: int
  machine_input: list[object]
  machine_output: list[object]
  machine_error_num: int = 0

  def device_id(self) -> int:
    """Get the unique device identifier for this pump."""
    return self.machine_id

  def parameter_id(self, param_name: str) -> int:
    """Get the parameter ID for a specific parameter name."""
    for params in [self.machine_input, self.machine_output]:
      for param in params:
        if param_name == param.var_name:
          return param.id if param.id is not None else 0
    return 0

  def input_list(self) -> list[object]:
    """Get the list of input parameters for pump control."""
    return self.machine_input

  def output_list(self) -> list[object]:
    """Get the list of output parameters for pump monitoring."""
    return self.machine_output

  def get_input_var_name(self) -> Iterator[Any]:
    """Get an iterator of input variable names."""
    for input_param in self.machine_input:
      yield input_param.var_name

  def get_output_var_name(self) -> Iterator[Any]:
    """Get an iterator of output variable names."""
    for output_param in self.machine_output:
      yield output_param.var_name

  def set_input_dict(self) -> Iterator[dict]:
    """Generate input variable dictionary for PLC communication."""
    for input_param in self.machine_input:
      if input_param.active:
        yield {input_param.var_name: [input_param.var_name_IN, "pyads." + input_param.data_type, 1]}

  def set_output_dict(self) -> Iterator[dict]:
    """Generate output variable dictionary for PLC communication."""
    for output_param in self.machine_output:
      if output_param.active:
        yield {output_param.var_name: [output_param.var_name_IN, "pyads." + output_param.data_type, 1]}

  def __str__(self) -> str:
    """String representation of the concrete pump."""
    return f"Machine ID: {self.machine_id}, Machine Input: {self.input_list}, Machine Output: {self.output_list}"


@dataclass
class DosingPumpHigh(Machine):
  """High-precision dosing pump for precise additive injection.

  The DosingPumpHigh class represents a high-precision dosing pump used for
  injecting additives, accelerators, or other chemicals into the concrete mix
  with high accuracy requirements.

  Attributes:
      machine_id (int): Unique identifier for this dosing pump instance.
      machine_input (List[object]): List of input parameter objects for dosing control.
      machine_output (List[object]): List of output parameter objects for dosing monitoring.
      machine_error_num (int): Current error count or error state indicator (default: 0).
  """

  machine_id: int
  machine_input: list[object]
  machine_output: list[object]
  machine_error_num: int = 0

  def device_id(self) -> int:
    """Get the unique device identifier for this dosing pump."""
    return self.machine_id

  def parameter_id(self, param_name: str) -> int:
    """Get the parameter ID for a specific parameter name."""
    for params in [self.machine_input, self.machine_output]:
      for param in params:
        if param_name == param.var_name:
          return param.id if param.id is not None else 0
    return 0

  def input_list(self) -> list[object]:
    """Get the list of input parameters for dosing control."""
    return self.machine_input

  def output_list(self) -> list[object]:
    """Get the list of output parameters for dosing monitoring."""
    return self.machine_output

  def get_input_var_name(self) -> Iterator[Any]:
    """Get an iterator of input variable names."""
    for input_param in self.machine_input:
      yield input_param.var_name

  def get_output_var_name(self) -> Iterator[Any]:
    """Get an iterator of output variable names."""
    for output_param in self.machine_output:
      yield output_param.var_name

  def set_input_dict(self) -> Iterator[dict]:
    """Generate input variable dictionary for PLC communication."""
    for input_param in self.machine_input:
      if input_param.active:
        yield {input_param.var_name: [input_param.var_name_IN, "pyads." + input_param.data_type, 1]}

  def set_output_dict(self) -> Iterator[dict]:
    """Generate output variable dictionary for PLC communication."""
    for output_param in self.machine_output:
      if output_param.active:
        yield {output_param.var_name: [output_param.var_name_IN, "pyads." + output_param.data_type, 1]}

  def __str__(self) -> str:
    """String representation of the high-precision dosing pump."""
    return f"Machine ID: {self.machine_id}, Machine Input: {self.input_list}, Machine Output: {self.output_list}"


@dataclass
class DosingPumpLow(Machine):
  """Low-precision dosing pump for bulk additive injection.

  The DosingPumpLow class represents a dosing pump used for injecting larger
  volumes of additives or materials where high precision is not critical.

  Attributes:
      machine_id (int): Unique identifier for this dosing pump instance.
      machine_input (List[object]): List of input parameter objects for dosing control.
      machine_output (List[object]): List of output parameter objects for dosing monitoring.
      machine_error_num (int): Current error count or error state indicator (default: 0).
  """

  machine_id: int
  machine_input: list[object]
  machine_output: list[object]
  machine_error_num: int = 0

  def device_id(self) -> int:
    """Get the unique device identifier for this dosing pump."""
    return self.machine_id

  def parameter_id(self, param_name: str) -> int:
    """Get the parameter ID for a specific parameter name."""
    for params in [self.machine_input, self.machine_output]:
      for param in params:
        if param_name == param.var_name:
          return param.id if param.id is not None else 0
    return 0

  def input_list(self) -> list[object]:
    """Get the list of input parameters for dosing control."""
    return self.machine_input

  def output_list(self) -> list[object]:
    """Get the list of output parameters for dosing monitoring."""
    return self.machine_output

  def get_input_var_name(self) -> Iterator[Any]:
    """Get an iterator of input variable names."""
    for input_param in self.machine_input:
      yield input_param.var_name

  def get_output_var_name(self) -> Iterator[Any]:
    """Get an iterator of output variable names."""
    for output_param in self.machine_output:
      yield output_param.var_name

  def set_input_dict(self) -> Iterator[dict]:
    """Generate input variable dictionary for PLC communication."""
    for input_param in self.machine_input:
      if input_param.active:
        yield {input_param.var_name: [input_param.var_name_IN, "pyads." + input_param.data_type, 1]}

  def set_output_dict(self) -> Iterator[dict]:
    """Generate output variable dictionary for PLC communication."""
    for output_param in self.machine_output:
      if output_param.active:
        yield {output_param.var_name: [output_param.var_name_IN, "pyads." + output_param.data_type, 1]}

  def __str__(self) -> str:
    """String representation of the low-precision dosing pump."""
    return f"Machine ID: {self.machine_id}, Machine Input: {self.input_list}, Machine Output: {self.output_list}"


@dataclass
class Controller(Machine):
  """System controller for coordinating multiple machine operations.

  The Controller class represents the main system controller that coordinates
  the operation of multiple machines in the digital casting system and manages
  global system parameters.

  Attributes:
      machine_id (int): Unique identifier for this controller instance.
      machine_input (List[object]): List of input parameter objects for system control.
      machine_output (List[object]): List of output parameter objects for system monitoring.
      machine_error_num (int): Current error count or error state indicator (default: 0).
  """

  machine_id: int
  machine_input: list[object]
  machine_output: list[object]
  machine_error_num: int = 0

  def device_id(self) -> int:
    """Get the unique device identifier for this controller."""
    return self.machine_id

  def parameter_id(self, param_name: str) -> int:
    """Get the parameter ID for a specific parameter name."""
    for params in [self.machine_input, self.machine_output]:
      for param in params:
        if param_name == param.var_name:
          return param.id if param.id is not None else 0
    return 0

  def input_list(self) -> list[object]:
    """Get the list of input parameters for system control."""
    return self.machine_input

  def output_list(self) -> list[object]:
    """Get the list of output parameters for system monitoring."""
    return self.machine_output

  def get_input_var_name(self) -> Iterator[Any]:
    """Get an iterator of input variable names."""
    for input_param in self.machine_input:
      yield input_param.var_name

  def get_output_var_name(self) -> Iterator[Any]:
    """Get an iterator of output variable names."""
    for output_param in self.machine_output:
      yield output_param.var_name

  def set_input_dict(self) -> Iterator[dict]:
    """Generate input variable dictionary for PLC communication."""
    for input_param in self.machine_input:
      if input_param.active:
        yield {input_param.var_name: [input_param.var_name_IN, "pyads." + input_param.data_type, 1]}

  def set_output_dict(self) -> Iterator[dict]:
    """Generate output variable dictionary for PLC communication."""
    for output_param in self.machine_output:
      if output_param.active:
        yield {output_param.var_name: [output_param.var_name_IN, "pyads." + output_param.data_type, 1]}

  def __str__(self) -> str:
    """String representation of the system controller."""
    return f"Machine ID: {self.machine_id}, Machine Input: {self.input_list}, Machine Output: {self.output_list}"
