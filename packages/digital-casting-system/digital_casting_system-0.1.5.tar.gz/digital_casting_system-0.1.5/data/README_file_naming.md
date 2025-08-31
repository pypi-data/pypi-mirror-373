# container for sample data files

## Structure of File name:
Date: year-month-day

_agg(%_aggregate): how much % aggregate of total volume

G: How much % gravel(core aggregate) of total aggregates(option)
S: spread [cm]
FW: flowrate of pump [L/min]
Temperature: Temperature monitoring experiment
rpm: impeller speed

EXAMPLE: 20230713_54agg_70S_1.5FW_TemperatureWithCAC

---

## Data sorting naming:
### Log
Data log order

### Inline mixer:
two motor system, M1 is motor 1, M2 is Motor 2 
- mixer_motor_temperature_M2
- mixer_motor_temperature_M1
- mixer_torque_M2
- mixer_torque_M1
- mixer_speed_M2
- mixer_speed_M1

### Funnel 
- mixer_temperature_Funnel_outlet
- mixer_temperature_Funnel
- mixer_temperature_Funnel_plate

### Concrete pump
- cp_temperature : concrete pump temperature
- cp_pressure : concrete pump pressure 
- cp_flowrate : concrete pump set flowrate

### Accelerator pump
- ac_flowrate : accelerator pump flowrate 

### Time
real time format : Min:Sec


