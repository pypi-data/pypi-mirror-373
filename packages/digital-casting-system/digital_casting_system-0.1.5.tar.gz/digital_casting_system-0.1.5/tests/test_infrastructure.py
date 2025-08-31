"""Test infrastructure configuration manager."""

from dcs.infrastructure.config_manager import ConfigManager


def test_config_manager_initialization():
  """Test that ConfigManager can be initialized."""
  config_manager = ConfigManager()
  assert config_manager is not None
  assert hasattr(config_manager, "_config_dir")


def test_config_manager_paths():
  """Test that ConfigManager has correct path structure."""
  config_manager = ConfigManager()
  assert config_manager._config_dir is not None
  assert config_manager._HOME is not None
  # The config directory should contain '_config' in its path
  assert "_config" in config_manager._config_dir
