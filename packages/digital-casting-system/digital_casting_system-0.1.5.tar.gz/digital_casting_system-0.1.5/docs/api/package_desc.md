# **Digital Casting System Package**

## Package Usage

> NOTE: WIP

Please find the detail of software architecture and API [here]()

## Package Descroption

#### Structure

```bash
src
└── dcs_dev
    ├── __init__.py
    ├── __main__.py # main entrance file
    ├── _config
    ├── abb_rob
    ├── data_processing
    ├── gui
    ├── hal
    ├── utilities
    ├── visualization
    ├── test_main_gui.py # test 
    ├── test_main_plc.py # test 
    └── test_main_rob.py # test 
```
#### Description

- **`data_processing`**: The class is to passing the processing data into system to covert plc raw data into research data.

- **`_config`**: The class is to provide the configuration file for robot(`abb_irb4600.json`) and plc(`beckhoff_controller.json`).

- **`abb_rob`**: The class is to provide the abb robot functions to connect the robot via `compas_rrc`.

- **`gui`**: The class is to create the GUI interface for user to interact with the system.

- **`hal`**: The abstract layter class is to convert the config file into python object.
  - `PLC`: The abstract class is to provide the functions to connect the PLC.
  - `Robot`: The abstract class is to handle to connect the robot.
  - `device`: The abstract class object to represnet the interface of the devices. 

- **`utilities`**: The class is to provide the utility functions for the system.

> NOTE: only support office data from json.
- `Visualization`: The class is to provide the visualization functions for the system. 

## Features
- More details about the package features
- Intergration with Robot package
    - define robot package
    - app gui user interface MOVE to cpp lib
    - for rhino user and gh user
    <!-- thinking how to read py lib into c++ a wrapper. -->

