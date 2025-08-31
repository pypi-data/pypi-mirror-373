from dataclasses import asdict, dataclass

# Serialization/Deserialization


@dataclass
class DataObject:
  """
  This moudle is the base data strcture to define the machine and its variables.

  var_id (str): variavle Id
  var_name (str)L variable name
  var_name_IN (str) variable name from plc, followed by plc naming
  is_write_value (bool): if the variable can be write to PLC
  is_read_value (bool): if the variable can be read form PLC
  data_type (str): data type in PLC, followed by C/C++ type
  active (bool): if the varible is active and can be read and/or write.

  """

  id: int
  var_name: str
  var_name_IN: str
  data_type: str
  active: bool

  def _to_dict(self) -> dict:
    return asdict(self)

  def __str__(self) -> str:
    return (
      f"id: {self.id} var_name: {self.var_name} var_name_IN: {self.var_name_IN} "
      f"data_type: {self.data_type} active: {self.active}"
    )


@dataclass
class DataParam:
  """
  This moudle is a data dictionary, which  wraps from DataObject with a machine id and params list.

  """

  machine_id: int
  machine_input: list[DataObject]
  machine_output: list[DataObject]

  def __getitem__(self, key: str) -> list[DataObject]:
    if key == "input":
      return [input_data for input_data in self.machine_input]
    elif key == "output":
      return [output_data for output_data in self.machine_output]
    else:
      raise KeyError(f"KeyError: {key}")

  def _to_dict(self) -> dict:
    return asdict(self)

  def __str__(self) -> str:
    return f"machine id: {self.machine_id} \
        \nmachine input: {self.machine_input} \
        \nmachine output: {self.machine_output}"


@dataclass
class MachineDataStruct:
  """
  This moudle is data structure, representing the machine.

  """

  machine_name: str
  machine_data: DataParam

  def _to_dict(self) -> dict:
    return asdict(self)
