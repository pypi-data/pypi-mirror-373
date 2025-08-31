import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from dcs.abb_rob.ros_client import DcsRosClient

if __name__ == "__main__":
  dcs_rob = DcsRosClient()

  dcs_rob._init_ros_client()

  dcs_rob._set_digital_output("doA061_MI1Enable", 0)

  dcs_rob._close_ros_client()
