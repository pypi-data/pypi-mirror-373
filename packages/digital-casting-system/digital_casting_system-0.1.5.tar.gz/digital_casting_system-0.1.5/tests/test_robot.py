"""Tests for DcsRosClient class."""

from unittest.mock import MagicMock, patch

import pytest

from dcs.robot.ros_client import DcsRosClient


@pytest.fixture
def mock_rrc():
  """Mock the compas_rrc module."""
  with patch("dcs.robot.ros_client.rrc") as mock_rrc:
    mock_ros_client = MagicMock()
    mock_abb_client = MagicMock()

    mock_rrc.RosClient.return_value = mock_ros_client
    mock_rrc.AbbClient.return_value = mock_abb_client

    # Mock common rrc classes
    mock_rrc.PrintText = MagicMock()
    mock_rrc.SetDigital = MagicMock()
    mock_rrc.ReadDigital = MagicMock()
    mock_rrc.MoveToFrame = MagicMock()
    mock_rrc.Motion.LINEAR = "LINEAR"

    yield mock_rrc


def test_init_ros_client(mock_rrc):
  """Test ROS client initialization."""
  client = DcsRosClient()
  client.ros = MagicMock()
  client.abb = MagicMock()

  with patch("builtins.print"):
    client.init_ros_client()

  mock_rrc.RosClient.assert_called_once()
  mock_rrc.AbbClient.assert_called_once_with(client.ros, "/rob1")
  client.ros.run.assert_called_once()
  client.abb.send_and_wait.assert_called_once()
  mock_rrc.PrintText.assert_called_once_with("Welcome to digital casting system")


def test_close_ros_client(mock_rrc):
  """Test ROS client cleanup."""
  client = DcsRosClient()
  client.ros = MagicMock()
  client.abb = MagicMock()

  with patch("builtins.print"):
    client.close_ros_client()

  client.ros.close.assert_called_once()
  client.ros.terminate.assert_called_once()


def test_set_digital_output(mock_rrc):
  """Test setting digital output."""
  client = DcsRosClient()
  client.abb = MagicMock()

  with patch("builtins.print"):
    client.set_digital_output("DO_Test", 1)

  mock_rrc.SetDigital.assert_called_once_with("DO_Test", 1)
  client.abb.send_and_wait.assert_called()


def test_get_digital_input(mock_rrc):
  """Test reading digital input."""
  client = DcsRosClient()
  client.abb = MagicMock()
  client.abb.send_and_wait.return_value = 1

  with patch("builtins.print"):
    client.get_digital_input("DI_Test")

  mock_rrc.ReadDigital.assert_called_once_with("DI_Test")
  client.abb.send_and_wait.assert_called()


def test_move_to_frame(mock_rrc):
  """Test frame movement."""
  client = DcsRosClient()
  client.abb = MagicMock()

  fake_frame = MagicMock()

  with patch("builtins.print"):
    client.move_to_frame(fake_frame, 100, 10)

  mock_rrc.MoveToFrame.assert_called_once_with(fake_frame, 100, 10, "LINEAR")
  client.abb.send.assert_called()


def test_get_robotarget_success(mock_rrc):
  """Test successful robotarget retrieval."""
  client = DcsRosClient()
  client.abb = MagicMock()

  expected_frame = MagicMock()
  expected_external = [0, 0, 0]
  client.abb.send_and_wait.return_value = (expected_frame, expected_external)

  frame, external_axes = client.get_robotarget()

  assert frame == expected_frame
  assert external_axes == expected_external


def test_get_robotarget_failure(mock_rrc):
  """Test robotarget retrieval failure."""
  client = DcsRosClient()
  client.abb = MagicMock()
  client.abb.send_and_wait.return_value = None

  with patch("builtins.print"):
    frame, external_axes = client.get_robotarget()

  assert frame is None
  assert external_axes is None


def test_print_text(mock_rrc):
  """Test text printing functionality."""
  client = DcsRosClient()
  client.abb = MagicMock()

  with patch("builtins.print") as mock_print:
    client.print_text("Test message")

  mock_rrc.PrintText.assert_called_once_with("Test message")
  client.abb.send.assert_called()
  mock_print.assert_called_once_with("Test message")
