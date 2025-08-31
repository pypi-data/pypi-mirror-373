# Digital Casting System

Digital Casting System (DCS) is a Python-based robotic digital casting control system that integrates ABB robots, Beckhoff PLCs, and inline mixing equipment for automated concrete casting. The system provides real-time monitoring, data recording, and robotic path control for industrial-scale digital casting operations.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Environment Setup

**NEVER CANCEL builds or long-running commands.** Build processes and dependency installations may take up to 45 minutes. Always use timeouts of 60+ minutes for build commands and 30+ minutes for test commands.

1. **Install UV Package Manager** (if not available):
   ```bash
   # Preferred method
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Fallback if curl fails due to network restrictions
   pip install uv
   ```

2. **Initialize Git Submodules** (1-2 seconds):
   ```bash
   git submodule init
   git submodule update
   ```

3. **Create Virtual Environment with Python 3.10** (30 seconds - NEVER CANCEL):
   ```bash
   uv venv --python 3.10 .venv
   source .venv/bin/activate  # Linux/Mac
   # or .venv\Scripts\activate  # Windows
   ```

4. **Install Dependencies** (17 seconds - NEVER CANCEL):
   ```bash
   uv pip install -e .
   ```

5. **Install Development Dependencies** (2 seconds):
   ```bash
   uv pip install .[dev]  # Installs black, isort, pytest, pytest-cov
   ```

6. **Install Documentation Dependencies** (5 seconds):
   ```bash
   uv pip install .[docs]  # Installs mkdocs, mkdocs-material, etc.
   
   # Install additional required docs plugins
   uv pip install markdown-exec mkdocs-include-markdown-plugin mkdocs-literate-nav
   ```

### Build and Test Commands

**CRITICAL**: Set timeout to 60+ minutes for ALL build commands. Set timeout to 30+ minutes for test commands.

1. **Run Linting** (0.02 seconds):
   ```bash
   ruff check  # Check for issues (66 code quality issues remain - these are non-critical)
   ruff check --fix  # Auto-fix 87 of 155 common issues (imports, formatting, etc.)
   ```
   
   **Note**: Remaining linting issues are primarily code quality concerns (unused variables, long lines, undefined names in test files) that do not prevent the application from running.

2. **Run Tests** (0.3 seconds):
   ```bash
   python -m pytest -v  # Run all tests
   python -m pytest tests/hal/ -v  # Run specific module tests
   ```

3. **Build Documentation** (1.5 seconds):
   ```bash
   mkdocs build  # Build static documentation
   mkdocs serve  # Serve docs locally at http://127.0.0.1:8000
   ```

4. **Start Virtual Robot Controller** (26 seconds - NEVER CANCEL):
   ```bash
   cd external_controllers/robot/docker_compas_rrc/virtual_controller
   docker compose up -d  # Start ROS master, bridge, and ABB driver
   docker compose ps     # Check container status
   docker compose down   # Stop containers when done
   ```

### Robot Communication

Robot communication works through Docker containers running ROS (Robot Operating System) with compas_rrc driver:

1. **Virtual Controller** (for development/testing):
   ```bash
   cd external_controllers/robot/docker_compas_rrc/virtual_controller
   docker compose up -d  # Starts 3 containers: ros-master, ros-bridge, abb-driver
   ```

2. **Real Controller** (for production with real ABB robot):
   ```bash
   cd external_controllers/robot/docker_compas_rrc/real_controller
   docker compose up -d
   ```

The containers provide:
- `ros-master`: ROS core at port 11311
- `ros-bridge`: WebSocket bridge at port 9090  
- `abb-driver`: ABB robot communication driver

### PLC Communication

PLC communication requires Beckhoff TwinCAT controller connection:

```python
from hal.plc import PLC
from hal.device import InlineMixer

# Example connection (requires actual PLC hardware)
plc = PLC(netid="5.57.158.168.1.1", ip="192.168.30.11")
plc.connect()  # Will fail without actual PLC hardware
```

**Note**: PLC functionality requires actual Beckhoff hardware and network connectivity.

## Validation

### Manual Validation Requirements

ALWAYS manually validate any new code changes by running through complete end-to-end scenarios:

1. **Environment Setup Validation**:
   ```bash
   # Verify complete environment setup
   uv --version  # Should show 0.8.13+
   source .venv/bin/activate
   python -c "import dcs_dev; print('Package imports successfully')"
   ```

2. **Code Quality Validation**:
   ```bash
   ruff check --fix  # Fix auto-fixable issues
   python -m pytest -v  # All tests must pass
   ```

3. **Robot Integration Test**:
   ```bash
   cd external_controllers/robot/docker_compas_rrc/virtual_controller
   docker compose up -d
   # Wait for containers to start (check with docker compose ps)
   
   # Test robot client connection (will show namespace errors - this is expected without proper robot configuration)
   cd ../../../../
   source .venv/bin/activate
   timeout 30 python src/dcs_dev/test_main_rob.py  # Expected: Shows "Cannot find the specified namespace" - this indicates the client is connecting to ROS but robot namespace needs configuration
   ```

4. **Documentation Build Test**:
   ```bash
   mkdocs build  # Must complete without errors
   mkdocs serve  # Verify docs are accessible
   ```

### Typical Development Workflow

1. **Setup**: Run environment setup commands above
2. **Development**: Make code changes
3. **Lint**: `ruff check --fix` 
4. **Test**: `python -m pytest -v`
5. **Robot Test**: Start Docker containers and test robot connectivity
6. **Documentation**: Update docs and run `mkdocs build`
7. **Commit**: Only commit after all validation steps pass

## Common Tasks

### Key Project Structure
```
src/dcs_dev/
├── __main__.py          # Main application entry point
├── abb_rob/            # ABB robot control (compas_rrc integration)
├── data_processing/    # Data handling and processing
├── gui/                # GUI application components
├── hal/                # Hardware abstraction layer (PLC, devices)
├── utilities/          # Utility functions
└── visualization/      # Data visualization tools

external_controllers/
├── robot/              # Robot Docker configurations
├── plc/                # PLC configuration files
└── machines/           # Machine configuration definitions

tests/
└── hal/                # Hardware abstraction tests
```

### Important Configuration Files

- `pyproject.toml`: Python project configuration, dependencies, and tool settings
- `mkdocs.yml`: Documentation configuration
- `external_controllers/robot/docker_compas_rrc/*/docker-compose.yml`: Robot controller setups

### Network and Hardware Requirements

- **Robot**: Requires Docker for virtual controller OR ABB robot hardware for real controller
- **PLC**: Requires Beckhoff TwinCAT controller and network connectivity (IP: 192.168.30.11)
- **Ports**: 
  - 11311: ROS master
  - 9090: ROS bridge websocket
  - Various PLC communication ports

### Build Time Expectations

- **Package Manager Install**: 0-30 seconds (varies by network)
- **Virtual Environment Creation**: 30 seconds (includes Python 3.10 download)
- **Dependencies Installation**: 17 seconds
- **Dev Dependencies**: 2 seconds  
- **Docs Dependencies**: 5 seconds
- **Test Execution**: 0.3 seconds
- **Linting**: 0.02 seconds
- **Documentation Build**: 1.5 seconds
- **Docker Robot Setup**: 26 seconds (first time with image download)

### Known Issues and Limitations

1. **Ruff Configuration**: Fixed invalid `indent-size` and `indent-style` in pyproject.toml
2. **Missing Docs Plugins**: Requires manual installation of `markdown-exec`, `mkdocs-include-markdown-plugin`, `mkdocs-literate-nav`
3. **PLC Hardware Dependency**: PLC testing requires actual hardware connection
4. **Docker Runtime**: Some environments may have Docker runtime issues with container creation
6. **Robot Connection Notes**: Robot scripts may show "Cannot find the specified namespace" errors when connecting - this is expected behavior when the robot namespace is not configured or hardware is not available. The connection attempt indicates the ROS bridge is working correctly.

### Emergency Commands

If something breaks during development:

```bash
# Reset virtual environment
rm -rf .venv
uv venv --python 3.10 .venv
source .venv/bin/activate
uv pip install -e .[dev,docs]

# Reset Docker containers
docker compose down
docker compose up -d

# Check system status
python -c "import dcs_dev; print('OK')"
ruff check
python -m pytest -v
mkdocs build
```

Always remember: **NEVER CANCEL long-running build processes**. They are expected to take significant time and will complete successfully.
