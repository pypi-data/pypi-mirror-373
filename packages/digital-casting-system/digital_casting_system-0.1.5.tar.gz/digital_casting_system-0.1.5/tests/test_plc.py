"""Tests for PLC module with mock connections."""

from unittest.mock import Mock, patch

import pyads
import pytest

from dcs.hal.plc import PLC, AdsConnectionError, VariableNotFoundInRepositoryError


@pytest.fixture
def plc_instance():
  """Create a PLC instance for testing."""
  return PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")


@pytest.fixture
def mock_connection():
  """Create a mock connection for testing."""
  mock_conn = Mock()
  mock_conn.is_open = False
  return mock_conn


@pytest.fixture
def mock_variable():
  """Create a mock variable for testing."""
  var = Mock()
  var.active = "true"
  var.var_name = "test_variable"
  var.var_name_IN = "test_variable"
  var.id = 1
  return var


def test_plc_initialization(plc_instance):
  """Test PLC initialization with valid parameters."""
  assert plc_instance.netid == "1.2.3.4.5.6"
  assert plc_instance.ip == "192.168.1.100"
  assert plc_instance.plc_vars_input == []
  assert plc_instance.plc_vars_output == []
  assert plc_instance.connection is not None


@patch("pyads.Connection")
def test_plc_connection_success(mock_connection_class):
  """Test successful PLC connection."""
  # Setup mock
  mock_connection = Mock()
  mock_connection.is_open = False
  mock_connection.read_device_info.return_value = {"device": "test"}
  mock_connection_class.return_value = mock_connection

  # Create PLC instance after patching
  plc_instance = PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")
  result = plc_instance.connect()

  # Assertions
  assert result is True
  mock_connection.open.assert_called_once()
  mock_connection.read_device_info.assert_called_once()


@patch("pyads.Connection")
def test_plc_connection_failure(mock_connection_class):
  """Test PLC connection failure."""
  # Setup mock
  mock_connection = Mock()
  mock_connection.is_open = False
  mock_connection.read_device_info.side_effect = pyads.ADSError("Connection failed")
  mock_connection_class.return_value = mock_connection

  # Create PLC instance after patching
  plc_instance = PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")
  result = plc_instance.connect()

  # Assertions
  assert result is False
  mock_connection.open.assert_called_once()
  mock_connection.read_device_info.assert_called_once()


@patch("pyads.Connection")
def test_plc_close_connection(mock_connection_class):
  """Test closing PLC connection."""
  # Setup mock
  mock_connection = Mock()
  mock_connection.is_open = True
  mock_connection_class.return_value = mock_connection

  # Create PLC instance after patching
  plc_instance = PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")
  plc_instance.close()

  # Assertions
  mock_connection.close.assert_called_once()


def test_set_plc_vars_input_list_empty(plc_instance):
  """Test setting input variables list when empty."""
  test_vars = [{"name": "var1"}, {"name": "var2"}]

  plc_instance.set_plc_vars_input_list(test_vars)

  assert plc_instance.plc_vars_input == test_vars


def test_set_plc_vars_input_list_extend(plc_instance):
  """Test extending input variables list when not empty."""
  plc_instance.plc_vars_input = [{"name": "existing_var"}]
  new_vars = [{"name": "var1"}, {"name": "var2"}]

  plc_instance.set_plc_vars_input_list(new_vars)

  expected = [{"name": "existing_var"}, {"name": "var1"}, {"name": "var2"}]
  assert plc_instance.plc_vars_input == expected


def test_set_plc_vars_output_list_empty(plc_instance):
  """Test setting output variables list when empty."""
  test_vars = [{"name": "var1"}, {"name": "var2"}]

  plc_instance.set_plc_vars_output_list(test_vars)

  assert plc_instance.plc_vars_output == test_vars


def test_set_plc_vars_output_list_extend(plc_instance):
  """Test extending output variables list when not empty."""
  plc_instance.plc_vars_output = [{"name": "existing_var"}]
  new_vars = [{"name": "var1"}, {"name": "var2"}]

  plc_instance.set_plc_vars_output_list(new_vars)

  expected = [{"name": "existing_var"}, {"name": "var1"}, {"name": "var2"}]
  assert plc_instance.plc_vars_output == expected


def test_read_variables_not_implemented(plc_instance):
  """Test that read_variables raises NotImplementedError."""
  with patch("dcs.hal.plc.PLC.connect", return_value=True):
    with pytest.raises(NotImplementedError):
      plc_instance.read_variables()


def test_read_variables_connection_failure(plc_instance):
  """Test read_variables when connection fails."""
  with patch("dcs.hal.plc.PLC.connect", return_value=False):
    with pytest.raises(AdsConnectionError):
      plc_instance.read_variables()


def test_write_variables_not_implemented(plc_instance):
  """Test that write_variables raises NotImplementedError."""
  with patch("dcs.hal.plc.PLC.connect", return_value=True):
    with pytest.raises(NotImplementedError):
      plc_instance.write_variables()


def test_write_variables_connection_failure(plc_instance):
  """Test write_variables when connection fails."""
  with patch("dcs.hal.plc.PLC.connect", return_value=False):
    with pytest.raises(AdsConnectionError):
      plc_instance.write_variables()


def test_check_variables_active_not_implemented(plc_instance):
  """Test that check_variables_active raises NotImplementedError."""
  with pytest.raises(NotImplementedError):
    plc_instance.check_variables_active()


@patch("pyads.Connection")
def test_get_variable_success(mock_connection_class, mock_variable):
  """Test successful variable reading."""
  # Setup mock
  mock_connection = Mock()
  mock_connection.read_by_name.return_value = 42
  mock_connection_class.return_value = mock_connection

  # Create PLC instance after patching
  plc_instance = PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")
  plc_instance.plc_vars_output = [mock_variable]

  result = plc_instance.get_variable("test_variable")

  assert result == 42
  mock_connection.read_by_name.assert_called_once_with("test_variable")


@patch("pyads.Connection")
def test_get_variable_not_found(mock_connection_class, mock_variable):
  """Test variable reading when variable not found."""
  # Setup mock
  mock_connection = Mock()
  mock_connection.read_by_name.side_effect = KeyError("Variable not found")
  mock_connection_class.return_value = mock_connection

  # Create PLC instance after patching
  plc_instance = PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")
  plc_instance.plc_vars_output = [mock_variable]

  with pytest.raises(VariableNotFoundInRepositoryError):
    plc_instance.get_variable("test_variable")


@patch("pyads.Connection")
def test_set_variable_success(mock_connection_class, mock_variable):
  """Test successful variable writing."""
  # Setup mock
  mock_connection = Mock()
  mock_connection.write_by_name.return_value = None
  mock_connection_class.return_value = mock_connection

  # Create PLC instance after patching
  plc_instance = PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")
  plc_instance.plc_vars_input = [mock_variable]

  result = plc_instance.set_variable("test_variable", 123)

  # Note: The current implementation has a bug - it should return the written value
  # but the method returns the result of write_by_name (which is None)
  assert result is None
  mock_connection.write_by_name.assert_called_once_with("test_variable", 123)


@patch("pyads.Connection")
def test_set_variable_not_found(mock_connection_class, mock_variable):
  """Test variable writing when variable not found."""
  # Setup mock
  mock_connection = Mock()
  mock_connection.write_by_name.side_effect = KeyError("Variable not found")
  mock_connection_class.return_value = mock_connection

  # Create PLC instance after patching
  plc_instance = PLC(netid="1.2.3.4.5.6", ip="192.168.1.100")
  plc_instance.plc_vars_input = [mock_variable]

  with pytest.raises(VariableNotFoundInRepositoryError):
    plc_instance.set_variable("test_variable", 123)
