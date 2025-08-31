import math

from compas.geometry import Frame

from dcs.robot.ros_client import DcsRosClient

ROBOT_ON = True
# Velocities
MOVE_SPEED = 100
MOVE_ZONE = 10

# Robot configuration
ROBOT_TOOL = "t_A061_InlineMixer"
ROBOT_WORK_OBJECT = "ob_A061_Wobjdata"


def rotate_vector(vector, angle):
  x = vector[0] * math.cos(angle) - vector[1] * math.sin(angle)
  y = vector[0] * math.sin(angle) + vector[1] * math.cos(angle)
  return [x, y, 0]


def main():
  # Create Ros Client
  rob_client = DcsRosClient()
  rob_client.init_ros_client()

  # Set Tool
  # rob_cleint._set_tool(ROBOT_TOOL)

  # Set Work Object
  rob_client._set_workobject(ROBOT_WORK_OBJECT)

  # Set Acceleration
  acc = 30  # Unit [%]
  ramp = 30  # Unit [%]
  rob_client._set_acceleration(acc, ramp)

  # Set Max Speed
  override = 100  # Unit [%]
  max_tcp = 1000  # Unit [mm/s]
  rob_client._set_max_speed(override, max_tcp)

  # ===========================================================================
  # Robot movement
  # ===========================================================================
  rob_client._print_text("Starting robotic movement.")

  # start = abb.send_and_wait(rrc.MoveToJoints(HOME_POSITION, EXTERNAL_AXES, MAX_SPEED, rrc.Zone.FINE))
  # home_position = [22.39, 39.56, -18.24, -209.02, -31.92, 222.16]
  # rob_cleint._move_to_joints(home_position, 0, MOVE_SPEED, 20)

  # Get Robtarget
  # home_position = [-15.35, -26.44, 54.56, -152.76, -22.91, 143.16]
  # startmsg = abb.send_and_wait(rrc.PrintText('PRINT START. Moving to home position'))

  # 1. Move robot to home position
  rob_client._print_text("Moving to home position")
  home_position = [-22.57, -15.64, 62.16, 77.41, 15.36, -94.05]
  rob_client._move_to_joints(home_position, 0, MOVE_SPEED, 20)
  frame, external_axes = rob_client._get_robotarget()
  print(frame, external_axes)

  # ==============================================================================
  # Define geometry
  # ==============================================================================

  # adjust for the formwork base on the calibration
  frame.point[0] = -480
  frame.point[1] = -920
  frame.point[2] = 1350

  x = frame.point[0]
  y = frame.point[1]
  z = frame.point[2]

  xaxis = [-1, 0, 0]
  yaxis = [0, 1, 0]
  angle_1 = math.radians(-45)
  angle_2 = math.radians(-90)

  frame_1 = Frame([x + 70, y, z], xaxis, yaxis)
  frame_2 = Frame([x, y - 840, z], rotate_vector(xaxis, angle_1), rotate_vector(yaxis, angle_1))
  frame_3 = Frame(
    [x - 860, y - 840 + 70, z],
    rotate_vector(xaxis, angle_2),
    rotate_vector(yaxis, angle_2),
  )

  frames = [frame_1, frame_2, frame_3, frame_2, frame_1]
  frames_list = frames * 1

  # ==============================================================================
  # Main robotic control function
  # ==============================================================================

  layer = 800
  for i in range(layer):
    for i, frame in enumerate(frames_list):
      rob_client.move_to_frame(frame, MOVE_SPEED, -1)
      rob_client._wait(2)

  # End of Code
  rob_client._print_text("Executing commands finished.")

  # Close client
  rob_client.close_ros_client()

  # 3. Move robot back to home position
  # endmsg = abb.send_and_wait(rrc.PrintText('PRINT END. Moving to home position'))
  # end = abb.send_and_wait(rrc.MoveToJoints(HOME_POSITION, EXTERNAL_AXES, MAX_SPEED, rrc.Zone.FINE))


if __name__ == "__main__":
  if not ROBOT_ON:
    print("Robot is off")
  main()
