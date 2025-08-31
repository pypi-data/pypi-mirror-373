"""Tests for integrated ConfigManager with data structures and HAL integration."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from dcs.data.struct import DataObject, DataParam
from dcs.hal.device import InlineMixer
from dcs.infrastructure.config_manager import ConfigManager


@pytest.fixture
def config_manager():
  """Create a ConfigManager instance for testing."""
  return ConfigManager()


@pytest.fixture
def sample_plc_config():
  """Create sample PLC configuration data."""
  return {
    "test_mixer": {
      "machine_id": "100",
      "input": [
        {
          "id": "101",
          "var_name": "mixer_enable",
          "var_name_IN": "GVL.b_mixer_enable",
          "data_type": "PLCTYPE_BOOL",
          "active": True,
        }
      ],
      "output": [
        {
          "id": "201",
          "var_name": "mixer_status",
          "var_name_IN": "GVL.b_mixer_status",
          "data_type": "PLCTYPE_BOOL",
          "active": True,
        }
      ],
    },
    "test_pump": {
      "machine_id": "200",
      "input": [],
      "output": [
        {
          "id": "301",
          "var_name": "pump_pressure",
          "var_name_IN": "GVL.f_pump_pressure",
          "data_type": "PLCTYPE_REAL",
          "active": True,
        }
      ],
    },
  }


@pytest.fixture
def temp_config_file(sample_plc_config):
  """Create a temporary config file for testing."""
  with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump(sample_plc_config, f)
    temp_path = f.name

  yield temp_path

  # Cleanup
  os.unlink(temp_path)


def test_config_manager_initialization(config_manager):
  """Test ConfigManager initializes with correct paths."""
  assert config_manager._HERE.endswith("infrastructure")
  assert config_manager._config_dir.endswith("_config")
  assert isinstance(config_manager.machines, dict)
  assert len(config_manager.machines) == 0


def test_get_robot_config_default_path(config_manager):
  """Test getting robot config from default path."""
  with patch("builtins.open"), patch("json.load") as mock_load:
    mock_load.return_value = {"robot_type": "ABB IRB4600"}

    result = config_manager.get_robot_config()

    assert result == {"robot_type": "ABB IRB4600"}


def test_get_robot_config_custom_path(config_manager, temp_config_file):
  """Test getting robot config from custom path."""
  result = config_manager.get_robot_config(temp_config_file)

  assert "test_mixer" in result
  assert "test_pump" in result


def test_get_plc_config_default_path(config_manager):
  """Test getting PLC config from default path."""
  with patch("builtins.open"), patch("json.load") as mock_load:
    mock_load.return_value = {"machine1": {"machine_id": "100"}}

    result = config_manager.get_plc_config()

    assert result == {"machine1": {"machine_id": "100"}}


def test_get_plc_config_custom_path(config_manager, temp_config_file):
  """Test getting PLC config from custom path."""
  result = config_manager.get_plc_config(temp_config_file)

  assert "test_mixer" in result
  assert "test_pump" in result


def test_load_plc_config_success(config_manager, temp_config_file):
  """Test successful loading of PLC config into structured data."""
  config_manager.load_plc_config(temp_config_file)

  assert len(config_manager.machines) == 2
  assert "test_mixer" in config_manager.machines
  assert "test_pump" in config_manager.machines

  # Verify structured data conversion
  mixer = config_manager.machines["test_mixer"]
  assert isinstance(mixer, DataParam)
  assert mixer.machine_id == 100
  assert len(mixer.machine_input) == 1
  assert len(mixer.machine_output) == 1

  # Verify DataObject structure
  input_var = mixer.machine_input[0]
  assert isinstance(input_var, DataObject)
  assert input_var.id == 101
  assert input_var.var_name == "mixer_enable"
  assert input_var.var_name_IN == "GVL.b_mixer_enable"
  assert input_var.data_type == "PLCTYPE_BOOL"
  assert input_var.active is True


def test_load_plc_config_file_not_found(config_manager):
  """Test loading PLC config with non-existent file."""
  with pytest.raises(FileNotFoundError):
    config_manager.load_plc_config("/nonexistent/path.json")


def test_load_plc_config_invalid_json(config_manager):
  """Test loading PLC config with invalid JSON."""
  with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    f.write("{ invalid json }")
    temp_path = f.name

  try:
    with pytest.raises(ValueError):
      config_manager.load_plc_config(temp_path)
  finally:
    os.unlink(temp_path)


def test_get_machine_success(config_manager, temp_config_file):
  """Test successful retrieval of machine configuration."""
  config_manager.load_plc_config(temp_config_file)

  mixer = config_manager.get_machine("test_mixer")

  assert isinstance(mixer, DataParam)
  assert mixer.machine_id == 100
  assert len(mixer.machine_input) == 1
  assert len(mixer.machine_output) == 1


def test_get_machine_not_loaded(config_manager):
  """Test getting machine when no configs are loaded."""
  with pytest.raises(RuntimeError, match="No machines loaded"):
    config_manager.get_machine("test_mixer")


def test_get_machine_not_found(config_manager, temp_config_file):
  """Test getting non-existent machine."""
  config_manager.load_plc_config(temp_config_file)

  with pytest.raises(KeyError, match="Machine 'nonexistent' not found"):
    config_manager.get_machine("nonexistent")


def test_get_all_machines_success(config_manager, temp_config_file):
  """Test getting all machine configurations."""
  config_manager.load_plc_config(temp_config_file)

  all_machines = config_manager.get_all_machines()

  assert len(all_machines) == 2
  assert "test_mixer" in all_machines
  assert "test_pump" in all_machines
  assert isinstance(all_machines["test_mixer"], DataParam)
  assert isinstance(all_machines["test_pump"], DataParam)


def test_get_all_machines_not_loaded(config_manager):
  """Test getting all machines when no configs are loaded."""
  with pytest.raises(RuntimeError, match="No machines loaded"):
    config_manager.get_all_machines()


def test_convert_to_data_param(config_manager, sample_plc_config):
  """Test conversion of raw config to DataParam object."""
  machine_data = sample_plc_config["test_mixer"]

  result = config_manager._convert_to_data_param(machine_data)

  assert isinstance(result, DataParam)
  assert result.machine_id == 100
  assert len(result.machine_input) == 1
  assert len(result.machine_output) == 1

  # Test input variable
  input_var = result.machine_input[0]
  assert input_var.id == 101
  assert input_var.var_name == "mixer_enable"

  # Test output variable
  output_var = result.machine_output[0]
  assert output_var.id == 201
  assert output_var.var_name == "mixer_status"


def test_convert_empty_inputs_outputs(config_manager):
  """Test conversion with empty input/output lists."""
  machine_data = {"machine_id": "300", "input": [], "output": []}

  result = config_manager._convert_to_data_param(machine_data)

  assert isinstance(result, DataParam)
  assert result.machine_id == 300
  assert len(result.machine_input) == 0
  assert len(result.machine_output) == 0


def test_hal_integration_with_config_manager(config_manager, temp_config_file):
  """Test integration between ConfigManager and HAL device classes."""
  config_manager.load_plc_config(temp_config_file)
  mixer_config = config_manager.get_machine("test_mixer")

  # Create InlineMixer using ConfigManager data
  inline_mixer = InlineMixer(mixer_config.machine_id, mixer_config.machine_input, mixer_config.machine_output)

  assert inline_mixer.device_id() == 100
  assert inline_mixer.parameter_id("mixer_enable") == 101
  assert inline_mixer.parameter_id("mixer_status") == 201

  # Test variable name retrieval
  input_names = inline_mixer.get_input_var_name()
  output_names = inline_mixer.get_output_var_name()

  assert "mixer_enable" in input_names
  assert "mixer_status" in output_names


def test_end_to_end_workflow(config_manager, temp_config_file):
  """Test complete end-to-end workflow from config loading to device usage."""
  # Step 1: Load configuration
  config_manager.load_plc_config(temp_config_file)

  # Step 2: Verify all machines loaded
  all_machines = config_manager.get_all_machines()
  assert len(all_machines) == 2

  # Step 3: Get specific machine
  mixer_config = config_manager.get_machine("test_mixer")
  pump_config = config_manager.get_machine("test_pump")

  # Step 4: Create devices using structured data
  mixer_device = InlineMixer(mixer_config.machine_id, mixer_config.machine_input, mixer_config.machine_output)

  # Step 5: Verify device functionality
  assert mixer_device.device_id() == 100
  assert len(mixer_device.input_list()) == 1
  assert len(mixer_device.output_list()) == 1

  # Step 6: Verify parameter access
  assert mixer_device.parameter_id("mixer_enable") == 101
  assert mixer_device.parameter_id("mixer_status") == 201
  assert mixer_device.parameter_id("nonexistent") == 0

  # Step 7: Verify variable name lists
  input_vars = mixer_device.get_input_var_name()
  output_vars = mixer_device.get_output_var_name()

  assert "mixer_enable" in input_vars
  assert "mixer_status" in output_vars


def test_config_manager_thread_safety(config_manager, temp_config_file):
  """Test that ConfigManager is safe for concurrent access."""
  import threading
  import time

  results = []
  errors = []

  def load_and_access():
    try:
      config_manager.load_plc_config(temp_config_file)
      machine = config_manager.get_machine("test_mixer")
      results.append(machine.machine_id)
    except Exception as e:
      errors.append(e)

  # Start multiple threads
  threads = []
  for _ in range(5):
    thread = threading.Thread(target=load_and_access)
    threads.append(thread)
    thread.start()

  # Wait for all threads to complete
  for thread in threads:
    thread.join()

  # Verify results
  assert len(errors) == 0, f"Errors occurred: {errors}"
  assert all(result == 100 for result in results)


def test_config_manager_memory_efficiency(config_manager, temp_config_file):
  """Test that ConfigManager efficiently manages memory."""
  # Load config multiple times
  for _ in range(10):
    config_manager.load_plc_config(temp_config_file)

  # Should still have same number of machines (not duplicated)
  all_machines = config_manager.get_all_machines()
  assert len(all_machines) == 2

  # Should be able to access machines without issues
  mixer = config_manager.get_machine("test_mixer")
  assert mixer.machine_id == 100
