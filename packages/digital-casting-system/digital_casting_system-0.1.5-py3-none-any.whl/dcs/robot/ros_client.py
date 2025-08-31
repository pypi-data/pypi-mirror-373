"""This module is a ROS client for ABB robot controller via compas_rrc."""

import compas_rrc as rrc


class DcsRosClient:
  """
  A ROS client for ABB robot controller via compas_rrc.

  This class provides an interface to connect, control, and communicate with an
  ABB robot controller using the compas_rrc library over ROS.
  It supports initialization and termination of the ROS client,
  digital/group/analog IO operations, and various robot movement commands.

  Attributes:
    _ros: Internal ROS client instance.
    _abb: Internal ABB client instance.
  """

  def __init__(self):
    """Initialize the ROS client.

    Creates a new DcsRosClient instance with uninitialized ROS and ABB client connections.
    """
    self._ros = None
    self._abb = None

  def init_ros_client(self) -> None:
    """Initialize the ROS client and establish connection to ABB robot.

    Creates and starts the ROS client connection, then initializes the ABB client
    with the robot namespace '/rob1'. Sends a welcome message to confirm connection.

    Raises:
        Exception: If ROS connection fails or ABB client initialization fails.
    """
    self.ros = rrc.RosClient()
    self.ros.run()
    self.abb = rrc.AbbClient(self.ros, "/rob1")

    print("Connected:", self.ros.is_connected)
    self.abb.send_and_wait(rrc.PrintText("Welcome to digital casting system"))

  def close_ros_client(self) -> None:
    """Close the ROS client and terminate the connection.

    Properly closes the ROS client connection and terminates the ROS communication.
    Sends a disconnection message before closing.
    """
    self.ros.close()
    self.ros.terminate()

    print("Connected:", self.ros.is_connected)
    self.abb.send_and_wait(rrc.PrintText("Disconnected to ROS"))

  #######################################################################
  # IO functions
  #######################################################################

  def set_digital_output(self, io_name: str, value: int) -> None:
    """Set the value of a digital output on the robot controller.

    Args:
        io_name (str): The name/identifier of the digital output signal.
        value (int): The value to set (typically 0 or 1 for digital signals).
    """
    self.abb.send_and_wait(rrc.SetDigital(io_name, value))
    print(f"{io_name} is set to {value}")

  def get_digital_input(self, io_name: str) -> None:
    """Retrieve and display the value of a digital input from the robot controller.

    Args:
        io_name (str): The name/identifier of the digital input signal to read.

    Side Effects:
        Prints the current value of the specified digital input to the console.
    """
    get_di = self.abb.send_and_wait(rrc.ReadDigital(io_name))
    print(f"{io_name} is {get_di}")

  def set_group_output(self, io_name: str, value: int) -> None:
    """Set the value of a group output on the robot controller.

    Group outputs allow setting multiple digital signals simultaneously.

    Args:
        io_name (str): The name/identifier of the group output.
        value (int): The integer value representing the group state.
    """
    self.abb.send_and_wait(rrc.SetGroup(io_name, value))
    print(f"{io_name} is {value}")

  def get_group_input(self, io_name: str) -> None:
    """Retrieve and display the value of a group input from the robot controller.

    Args:
        io_name (str): The name/identifier of the group input to read.

    Side Effects:
        Prints the current value of the specified group input to the console.
    """
    get_gi = self.abb.send_and_wait(rrc.ReadGroup(io_name))
    print(f"{io_name} is {get_gi}")

  def get_analog_output(self, io_name: str, value: int) -> None:
    """Set the value of an analog output on the robot controller.

    Note: Method name suggests 'get' but actually sets the analog output value.

    Args:
        io_name (str): The name/identifier of the analog output signal.
        value (int): The analog value to set.
    """
    get_ao = self.abb.send_and_wait(rrc.SetAnalog(io_name, value))
    print(f"{io_name} is {get_ao}")

  def get_analog_input(self, io_name: str) -> None:
    """Retrieve and display the value of an analog input from the robot controller.

    Args:
        io_name (str): The name/identifier of the analog input to read.

    Side Effects:
        Prints the current value of the specified analog input to the console.
    """
    get_ai = self.abb.send_and_wait(rrc.ReadAnalog(io_name))
    print(f"{io_name} is {get_ai}")

  #######################################################################
  # movement functions
  #######################################################################
  def move_to_frame(self, frame, speed: int, zone: int) -> None:
    """Move the robot to a specified frame using linear motion.

    Args:
        frame: The target frame/pose for the robot to move to.
        speed (int): Movement speed parameter.
        zone (int): Zone parameter controlling path precision vs speed.

    Side Effects:
        Sends movement command to robot and prints movement status.
    """
    self.abb.send(rrc.MoveToFrame(frame, speed, zone, rrc.Motion.LINEAR))
    print(f"Robot is moving to {frame}")

  def move_to_robotarget(self):
    """Move the robot to a robot target position.

    Raises:
        NotImplementedError: This method is not yet implemented.
    """
    raise NotImplementedError

  def move_to_joints(self, joints: list, external_axes, speed: int, zone: int) -> None:
    """Move the robot to specified joint positions.

    Args:
        joints (list): List of joint angles for robot axes.
        external_axes: External axis positions (if applicable).
        speed (int): Movement speed parameter.
        zone (int): Zone parameter controlling path precision vs speed.

    Side Effects:
        Sends joint movement command to robot and prints movement status.
    """
    self.abb.send(rrc.MoveToJoints(joints, external_axes, speed, zone))
    print(f"Robot is moving to {joints}")

  def wait(self, time: int) -> None:
    """Make the robot wait for a specified duration.

    Args:
        time (int): Wait time duration (units depend on robot controller settings).
    """
    self.abb.send(rrc.WaitTime(time))

  def set_move_zone(self, zone: int) -> None:
    """Set the movement zone parameter for robot motions.

    Args:
        zone (int): Zone parameter value.

    Raises:
        NotImplementedError: This method is not yet implemented.
    """
    raise NotImplementedError

  def set_acceleration(self, acc: int, ramp: int) -> None:
    """Set the robot's acceleration parameters.

    Args:
        acc (int): Acceleration value as percentage (%).
        ramp (int): Ramp value as percentage (%).
    """
    self.abb.send(rrc.SetAcceleration(acc, ramp))

  def set_max_speed(self, overide: int, max_tcp: int) -> None:
    """Set the robot's maximum speed parameters.

    Args:
        overide (int): Speed override value as percentage (%).
        max_tcp (int): Maximum TCP (Tool Center Point) speed in mm/s.
    """
    self.abb.send(rrc.SetMaxSpeed(overide, max_tcp))

  def set_tool(self, tool_name: str) -> None:
    """Set the active tool for the robot.

    Args:
        tool_name (str): Name of the tool to activate.

    Side Effects:
        Prints confirmation of tool change.
    """
    self.abb.send(rrc.SetTool(tool_name))
    print(f"Tool is set to {tool_name}")

  def _get_tool(self):
    """Get the currently active tool.

    Raises:
        NotImplementedError: This method is not yet implemented.
    """
    raise NotImplementedError

  def set_workobject(self, workobject: str) -> None:
    """Set the active work object coordinate system for the robot.

    Args:
        workobject (str): Name of the work object to activate.

    Side Effects:
        Prints confirmation of work object change.
    """
    self.abb.send(rrc.SetWorkObject(workobject))
    print(f"Workobject is set to {workobject}")

  def get_workobject(self):
    """Get the currently active work object.

    Raises:
        NotImplementedError: This method is not yet implemented.
    """
    raise NotImplementedError

  def get_robotarget(self) -> tuple:
    """Get the current robot target position and external axes.

    Returns:
        tuple: A tuple containing (frame, external_axes) representing the current
               robot position, or (None, None) if the request fails.
    """
    result = self.abb.send_and_wait(rrc.GetRobtarget())
    if result is None:
      print("Failed to get robotarget: result is None")
      return None, None
    frame, external_axes = result
    return frame, external_axes

  def print_text(self, text: str) -> None:
    """Send text to be printed on the robot controller and console.

    Args:
        text (str): The text message to print.

    Side Effects:
        Sends print command to robot controller and prints to local console.
    """
    self.abb.send(rrc.PrintText(text))
    print(text)
