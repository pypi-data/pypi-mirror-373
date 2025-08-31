# ARCHITECTURE

## Infrastructure Layer
Device Drivers
HAL (Hardware Abstraction Layer) - Interfaces with physical devices
PLCDriver : Communicates with the PLC
DeviceDriver : Base class for all device drivers
MixerDriver , PumpDriver , etc.: Specific device implementations

Repository
Data Storage - Handles persistence concerns
MeasurementRepository : Stores and retrieves measurement data
SessionRepository : Manages recording sessions
ConfigurationRepository : Handles system configuration

Messaging Service
Event Bus - Enables communication between components
EventBus : Core event publishing/subscribing mechanism
EventTypes : Definitions of system events
MessageSerializer : Handles message formatting

## Domain Layer
Device Model
Business Entities - Core domain objects
Device : Base class for all devices
Mixer , Pump , Sensor : Domain models for specific device types
DeviceStatus : Value object for device state

Measurements
Data Models - Represents collected data
Measurement : Base class for measurements
TemperatureMeasurement , PressureMeasurement , etc.
MeasurementBatch : Collection of related measurements

Casting Process
Process Logic - Business rules and workflow
ProcessStep : Represents a step in the casting process
ProcessController : Manages the overall process flow
ProcessValidator : Validates process constraints

## Application Layer
Session Manager
Session Control - Manages recording sessions
SessionService : Creates, monitors, and ends sessions
SessionState : Tracks the state of active sessions
SessionConfiguration : Handles session-specific settings

Data Logger
Logging Service - Handles data collection and logging
DataCollector : Collects data from devices
DataProcessor : Processes raw data
DataPersister : Saves processed data

System Monitor
Monitoring Service - Monitors system health
SystemHealthCheck : Verifies system components
AlertService : Generates alerts for abnormal conditions
PerformanceTracker : Tracks system performance
