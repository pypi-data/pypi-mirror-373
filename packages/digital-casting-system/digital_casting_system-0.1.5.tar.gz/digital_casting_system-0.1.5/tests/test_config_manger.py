import json
import os
from pathlib import Path

import pytest

from dcs.infrastructure.config_manager import ConfigManager


@pytest.fixture
def config_manager():
  """Fixture to create ConfigManager instance for testing."""
  return ConfigManager()


def test_config_manager_initialization(config_manager):
  """Test ConfigManager initialization and path setup."""
  assert hasattr(config_manager, "_HERE")
  assert hasattr(config_manager, "_HOME")
  assert hasattr(config_manager, "_config_dir")
  assert os.path.isabs(config_manager._HOME)
  assert os.path.isabs(config_manager._config_dir)


def test_robot_config_matches_file(config_manager):
  """Ensure get_robot_config() returns the same dict as the abb json file."""
  loaded = config_manager.get_robot_config()
  file_path = Path(str(config_manager._config_dir)) / "abb_irb4600.json"
  assert os.path.exists(file_path), f"Config file not found: {file_path}"
  with open(file_path, encoding="utf-8") as f:
    expected = json.load(f)
  assert loaded == expected


def test_plc_config_matches_file(config_manager):
  """Ensure get_plc_config() returns the same dict as the beckhoff json file."""
  loaded = config_manager.get_plc_config()
  file_path = Path(str(config_manager._config_dir)) / "beckhoff_controller.json"
  assert os.path.exists(file_path), f"Config file not found: {file_path}"
  with open(file_path, encoding="utf-8") as f:
    expected = json.load(f)
  assert loaded == expected
