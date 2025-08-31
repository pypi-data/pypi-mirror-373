"""Real-time data collection example using unified configuration management.

This example demonstrates the complete real-time digital casting system workflow
using the unified ConfigManager API for PLC communication and data recording.

The example showcases:
1. Unified configuration management for real-time operations
2. Real PLC connection and data collection
3. Multi-threaded data recording from all devices
4. Continuous monitoring and data export
5. Integration between ConfigManager, HAL devices, and PLC communication

This follows the logic from __main__.py but uses the new unified ConfigManager
approach instead of the legacy DataHandler.

Usage:
    python examples/realtime_example.py

Requirements:
    - Beckhoff PLC hardware connected and configured
    - Network connectivity to PLC (IP: 192.168.30.11)
    - Proper PLC variable configuration
"""

import os
import time
from datetime import datetime
from threading import Thread

from dcs.data.processing import DataGathering
from dcs.hal.device import (
  ConcretePump,
  Controller,
  DosingPumpHigh,
  DosingPumpLow,
  InlineMixer,
)
from dcs.hal.plc import PLC
from dcs.infrastructure.config_manager import ConfigManager

# =================================================================================
"""Global Configuration Values"""

CLIENT_ID = "5.57.158.168.1.1"  # PLC AMSNETID
CLIENT_IP = "192.168.30.11"
NOW_DATE = datetime.now().date().strftime("%Y%m%d")  # Date

######################## File Configuration ######################
# TODO: Add input function for filename configuration
DEFAULT_FILENAME = NOW_DATE + "_" + "unified_system_realtime"

# Directory paths
HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))

JSON_DIR = os.path.join(DATA, "json")
CSV_DIR = os.path.join(DATA, "csv")

# Operational flags
REAL_PLC = True  # Set to False for offline testing
DRY_RUN = False  # Set to True for testing without actual mixing
RECORDED_DELAY_TIME = 1  # Data recording interval in seconds
LOOP_TIME = 10  # Main loop interval


def read_from_plc_and_store(data: dict, key: str, plc_variable: str, plc_connection: PLC):
  """Thread-safe function to read PLC variable and store in data dictionary.

  Args:
      data: Dictionary to store the read value
      key: Key name for the data dictionary
      plc_variable: PLC variable name to read
      plc_connection: PLC connection instance
  """
  try:
    r_value_plc = plc_connection.get_variable(plc_variable)

    # Apply scaling for temperature and pressure values
    if "temperature" in plc_variable.lower() or "pressure" in plc_variable.lower():
      r_value_plc /= 10
    elif isinstance(r_value_plc, float):
      r_value_plc = round(r_value_plc, 2)

    data[key] = r_value_plc
  except Exception as e:
    print(f"Error reading PLC variable {plc_variable}: {e}")
    data[key] = None


def setup_devices_with_unified_config():
  """Setup all devices using the unified ConfigManager approach.

  Returns:
      tuple: (devices_dict, all_params_dict) containing device instances and parameter lists
  """
  print("Setting up devices with unified configuration management...")

  # Initialize ConfigManager and load all configurations
  config = ConfigManager()
  config.load_plc_config()
  print("✓ All PLC configurations loaded into memory")

  devices = {}
  all_params = {}

  # Create InlineMixer using unified config
  try:
    mixer_config = config.get_machine("inline_mixer")
    inline_mixer = InlineMixer(
      mixer_config.machine_id,
      mixer_config.machine_input,
      mixer_config.machine_output,
    )
    devices["inline_mixer"] = inline_mixer

    # Get parameter lists for data collection
    mixer_params_output = [param for param in inline_mixer.set_output_dict()]
    mixer_params_input = [param for param in inline_mixer.set_input_dict()]
    all_params["inline_mixer"] = mixer_params_output + mixer_params_input

    print(f"✓ InlineMixer created (ID: {inline_mixer.device_id()})")
  except Exception as e:
    print(f"✗ Failed to create InlineMixer: {e}")
    return None, None

  # Create ConcretePump
  try:
    pump_config = config.get_machine("concrete_pump")
    concrete_pump = ConcretePump(
      pump_config.machine_id,
      pump_config.machine_input,
      pump_config.machine_output,
    )
    devices["concrete_pump"] = concrete_pump

    pump_params_output = [param for param in concrete_pump.set_output_dict()]
    pump_params_input = [param for param in concrete_pump.set_input_dict()]
    all_params["concrete_pump"] = pump_params_output + pump_params_input

    print(f"✓ ConcretePump created (ID: {concrete_pump.device_id()})")
  except Exception as e:
    print(f"✗ Failed to create ConcretePump: {e}")

  # Create DosingPumpHigh (Accelerator pump)
  try:
    dosing_high_config = config.get_machine("dosing_pump_high")
    accelerator_pump = DosingPumpHigh(
      dosing_high_config.machine_id,
      dosing_high_config.machine_input,
      dosing_high_config.machine_output,
    )
    devices["dosing_pump_high"] = accelerator_pump

    accel_params_output = [param for param in accelerator_pump.set_output_dict()]
    accel_params_input = [param for param in accelerator_pump.set_input_dict()]
    all_params["dosing_pump_high"] = accel_params_output + accel_params_input

    print(f"✓ DosingPumpHigh created (ID: {accelerator_pump.device_id()})")
  except Exception as e:
    print(f"✗ Failed to create DosingPumpHigh: {e}")

  # Create DosingPumpLow (Superplasticizer pump)
  try:
    dosing_low_config = config.get_machine("dosing_pump_low")
    superplasticizer_pump = DosingPumpLow(
      dosing_low_config.machine_id,
      dosing_low_config.machine_input,
      dosing_low_config.machine_output,
    )
    devices["dosing_pump_low"] = superplasticizer_pump

    super_params_output = [param for param in superplasticizer_pump.set_output_dict()]
    super_params_input = [param for param in superplasticizer_pump.set_input_dict()]
    all_params["dosing_pump_low"] = super_params_output + super_params_input

    print(f"✓ DosingPumpLow created (ID: {superplasticizer_pump.device_id()})")
  except Exception as e:
    print(f"✗ Failed to create DosingPumpLow: {e}")

  # Create Controller (System controller)
  try:
    system_config = config.get_machine("system")
    concrete_controller = Controller(
      system_config.machine_id,
      system_config.machine_input,
      system_config.machine_output,
    )
    devices["system"] = concrete_controller

    controller_params_output = [param for param in concrete_controller.set_output_dict()]
    controller_params_input = [param for param in concrete_controller.set_input_dict()]
    all_params["system"] = controller_params_output + controller_params_input

    print(f"✓ Controller created (ID: {concrete_controller.device_id()})")
  except Exception as e:
    print(f"✗ Failed to create Controller: {e}")

  return devices, all_params


def initialize_plc_variables(plc_connection: PLC, devices: dict):
  """Initialize PLC variable lists for all devices.

  Args:
      plc_connection: PLC connection instance
      devices: Dictionary of device instances
  """
  print("Initializing PLC variables for all devices...")

  for device_name, device in devices.items():
    try:
      # Set input and output variable lists for each device
      plc_connection.set_plc_vars_input_list(device.input_list())
      plc_connection.set_plc_vars_output_list(device.output_list())
      print(f"✓ PLC variables initialized for {device_name}")
    except Exception as e:
      print(f"✗ Failed to initialize PLC variables for {device_name}: {e}")


def run_realtime_data_collection(plc_connection: PLC, devices: dict, all_params: dict):
  """Run the main real-time data collection loop.

  Args:
      plc_connection: PLC connection instance
      devices: Dictionary of device instances
      all_params: Dictionary of parameter lists for each device
  """
  print("Starting real-time data collection...")

  if DRY_RUN:
    print("DRY_RUN mode: Simulating data collection without actual mixing")
    return

  # Get control parameters from the devices
  inline_mixer = devices.get("inline_mixer")
  concrete_controller = devices.get("system")

  if not inline_mixer or not concrete_controller:
    print("✗ Required devices (inline_mixer, system) not available")
    return

  # Get control parameters for monitoring
  mixer_output_params = all_params["inline_mixer"]
  controller_input_params = all_params["system"]

  # Find specific control variables
  param_mixer_is_run = None
  param_data_recording = None

  for param in mixer_output_params:
    if "mixer_is_run" in param:
      param_mixer_is_run = param
      break

  for param in controller_input_params:
    if "controller_data_recording" in param:
      param_data_recording = param
      break

  if not param_mixer_is_run or not param_data_recording:
    print("✗ Required control parameters not found in device configuration")
    return

  # Initialize monitoring variables
  counter = 0
  recording_data = {}

  # Get initial status
  try:
    data_is_recording = plc_connection.get_variable(param_data_recording["controller_data_recording"][0])
    print(f"Initial recording status: {data_is_recording}")
  except Exception as e:
    print(f"✗ Failed to read initial PLC variables: {e}")
    return

  # Initialize data recorder
  data_recorder = DataGathering(DEFAULT_FILENAME)

  print("Entering main data collection loop...")
  print("Monitoring PLC for data recording trigger...")

  # Main data collection loop
  while data_is_recording:
    try:
      counter += 1
      log_id = counter

      # Update timestamp
      now_time = datetime.now().time().strftime("%H:%M:%S.%f")[:-3]

      # Initialize data structure for this collection cycle
      recording_data[log_id] = {"Time": now_time}

      print(f"Data collection cycle {log_id} at {now_time}")

      # Collect data from all devices using threading for parallel processing
      threads = []

      # Collect data from each device
      for device_name, params_list in all_params.items():
        for params in params_list:
          for key, value in params.items():
            thread = Thread(
              target=read_from_plc_and_store,
              args=(recording_data[log_id], key, value[0], plc_connection),
            )
            thread.start()
            threads.append(thread)

      # Wait for all threads to complete (with timeout)
      for thread in threads:
        thread.join(timeout=2.0)  # 2 second timeout per thread

      # Delay between recordings
      time.sleep(RECORDED_DELAY_TIME)

      # Write data to JSON file
      data_recorder.write_dict_to_json(recording_data)

      # Update monitoring variables
      data_is_recording = plc_connection.get_variable(param_data_recording["controller_data_recording"][0])

      # Check if recording should stop
      if not data_is_recording:
        print("Recording stopped by PLC signal")
        break

    except Exception as e:
      print(f"Error during data collection cycle {counter}: {e}")
      continue

  print("Data collection completed")

  # Process and save final data to CSV
  if recording_data:
    print("Processing collected data for CSV export...")

    recording_data_for_csv = []
    for log_id, data in recording_data.items():
      data["Log"] = log_id  # Add log ID as column
      recording_data_for_csv.append(data)

    # Create header from first data entry
    if recording_data_for_csv:
      header = list(recording_data_for_csv[0].keys())
      header.reverse()  # Match original order

      # Save to CSV file
      data_recorder.write_dict_to_csv(recording_data_for_csv, header)
      print(f"✓ Data saved to CSV with {len(recording_data_for_csv)} records")

  # Close PLC connection
  try:
    plc_connection.close()
    print("✓ PLC connection closed")
  except Exception as e:
    print(f"Warning: Error closing PLC connection: {e}")


def main():
  """Main execution function for real-time data collection system."""
  print("=" * 80)
  print("Digital Casting System - Real-time Data Collection")
  print("Using Unified Configuration Management")
  print("=" * 80)

  # Setup devices using unified configuration management
  devices, all_params = setup_devices_with_unified_config()

  if not devices or not all_params:
    print("✗ Failed to setup devices. Cannot proceed.")
    return

  print(f"\n✓ Successfully created {len(devices)} devices")
  for device_name in devices.keys():
    print(f"  • {device_name}")

  if REAL_PLC:
    print(f"\nConnecting to PLC at {CLIENT_IP} (NetID: {CLIENT_ID})...")

    try:
      # Create and connect to PLC
      plc = PLC(netid=CLIENT_ID, ip=CLIENT_IP)
      plc.connect()
      print("✓ PLC connection established")

      # Initialize PLC variables for all devices
      initialize_plc_variables(plc, devices)

      # Start real-time data collection
      run_realtime_data_collection(plc, devices, all_params)

    except Exception as e:
      print(f"✗ PLC connection or operation failed: {e}")
      print("This is expected if PLC hardware is not available")

  else:
    print("\nOffline mode: PLC connection disabled")
    print("Enable REAL_PLC = True for actual PLC communication")

  print("\n" + "=" * 80)
  print("System Benefits - Unified Configuration in Real-time Operations")
  print("=" * 80)

  print("\n✓ Key Improvements:")
  print("  • Single ConfigManager replaces DataHandler for device setup")
  print("  • All machine configurations loaded into memory once")
  print("  • Type-safe structured data objects (DataParam/DataObject)")
  print("  • Consistent device creation pattern across all machine types")
  print("  • Maintained threading and real-time performance")
  print("  • Backward compatible with existing PLC communication")

  print("\n💡 Unified Workflow:")
  print("  1. ConfigManager loads all PLC configurations into memory")
  print("  2. Devices created using: config.get_machine() → Device()")
  print("  3. PLC variables initialized for all devices")
  print("  4. Real-time data collection with multi-threading")
  print("  5. Data export to JSON and CSV formats")

  print("\n🔧 Configuration Management:")
  print("  • Eliminates duplication between ConfigManager and DataHandler")
  print("  • Centralizes all machine parameters in memory")
  print("  • Provides clean API for device creation and management")
  print("  • Thread-safe access to configuration data")

  print(f"\n{'=' * 80}")
  print("Real-time Data Collection Complete!")
  print(f"{'=' * 80}\n")


if __name__ == "__main__":
  """Entry point for real-time data collection with unified configuration."""
  main()
