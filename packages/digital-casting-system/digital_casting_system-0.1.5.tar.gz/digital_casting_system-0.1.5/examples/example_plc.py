"""Example demonstrating PLC configuration management and device interaction.

This example shows how to use the unified ConfigManager to load machine
configurations and work with device classes for PLC communication.
"""

from dcs.hal.device import InlineMixer
from dcs.infrastructure.config_manager import ConfigManager

if __name__ == "__main__":
  # Initialize the configuration manager
  config_manager = ConfigManager()
  print("ConfigManager initialized")
  print(f"Config directory: {config_manager._config_dir}")

  # Load all PLC machine configurations into memory
  config_manager.load_plc_config()
  print("PLC configurations loaded into memory")

  # Get all available machines
  all_machines = config_manager.get_all_machines()
  print(f"Available machines: {list(all_machines.keys())}")

  # Get the inline mixer configuration
  inline_mixer_config = config_manager.get_machine("inline_mixer")
  print(f"Inline mixer machine ID: {inline_mixer_config.machine_id}")

  # Create the InlineMixer device using the structured configuration
  inline_mixer = InlineMixer(
    inline_mixer_config.machine_id,
    inline_mixer_config.machine_input,
    inline_mixer_config.machine_output,
  )

  # Demonstrate device functionality
  print(f"Device ID: {inline_mixer.device_id()}")
  print(f"Parameter ID for 'mixer_is_run': {inline_mixer.parameter_id('mixer_is_run')}")

  print("\nInput variables:")
  for input_var in inline_mixer.get_input_var_name():
    print(f"  {input_var}")

  print("\nOutput variables:")
  for output_var in inline_mixer.get_output_var_name():
    print(f"  {output_var}")

  print("\nExample complete - ConfigManager successfully integrated with HAL devices")
