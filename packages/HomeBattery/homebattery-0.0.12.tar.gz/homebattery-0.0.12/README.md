# HomeBattery

## Overview

This project provides a set of Python modules to interact with various inverters and battery management systems. The modules allow for reading and writing parameters such as power setpoints, battery state of charge, and grid voltage.

## Features

- Support for multiple inverter brands:

  - Victron

  - Huawei

  - Deye (via Modbus and Solarman data logger)

  - Sessy

  - SMA

- Communication via Modbus TCP

- Reading and writing inverter and battery parameters

- Asynchronous API support for Sessy battery system

- Comprehensive register mapping for each inverter

## Tested Devices

The following devices have been used to test the implementations in this project:

- **Victron Inverter**: Victron MultiPlus-II
- **Huawei SUN2000 Inverter**: Huawei SUN2000-6KTL-M1
- **Deye Inverter**: Deye 12K-SG04LP3-EU
- **Sessy Battery System**: Sessy
- **SMA Inverter**: Sunny island 8.0H-13

## Installation

For PyPi installation please run:

```bash
python3 -m pip install HomeBattery
```

For local installation please run this command:

```bash
python3 -m pip install .
```

## Usage

Example usage for interacting with a Victron inverter:

> **Warning**: Using this library to interact with your inverters and battery systems may result in the loss of settings or configurations. Ensure you have backed up all important settings before proceeding. Use this library at your own risk.

```python
from HomeBattery import VictronInverter

# Initialize the Victron inverter
victron_inverter = VictronInverter(ip="192.168.1.100", port=502)

# Read active power
active_power = victron_inverter.get_active_power()
print(f"Active Power: {active_power} W")

# Read battery state of charge (SOC)
battery_soc = victron_inverter.get_battery_soc()
print(f"Battery SOC: {battery_soc} %")

# Read grid voltage
grid_voltage = victron_inverter.get_phase_voltage(phase=1)
print(f"Grid Voltage: {grid_voltage} V")

# Set power setpoint
victron_inverter.set_power_setpoint(1500)
print("Power setpoint set to 1500 W on phase 1")
```


## Modules

### 1. `modbus.py`

Contains utility classes for interacting with Modbus devices:

- **ModbusDevice**: Base class for Modbus communication. This class provides the foundational methods and properties required to communicate with Modbus devices. It handles the setup of communication parameters, sending and receiving Modbus requests, and processing responses.

- **Register**: Data class that encapsulates the properties and behaviors of a Modbus register, providing methods to decode and build payloads based on the register's data type and other attributes.

- **AccessType** and **DataType**: Enums for defining register properties. `AccessType` specifies the read/write access for a register, while `DataType` Defines the type of data stored in the register.

### 2. `battery.py`

Defines battery management classes:

- **Battery**: Base battery class

- **ModbusBattery**: Extends Battery to support Modbus communication

### 3. `victron.py`

Handles communication with **Victron inverters**:

- Inherits from `ModbusBattery`

- Supports reading active power, battery SOC, and grid voltage

- Allows setting power and current setpoints

- Implements comprehensive register mapping

### 4. `sun2000.py`

Handles communication with **Sun2000 inverters**:

- Inherits from `ModbusBattery`

- Supports reading active power, battery SOC, and grid voltage

- Allows setting power and current setpoints

- Implements comprehensive register mapping

### 5. `deye_modbus.py`

Handles communication with **Deye inverters** via Modbus:

- Inherits from `ModbusBattery`

- Supports reading active power, battery SOC, and grid voltage

- Allows setting power and current setpoints

- Implements comprehensive register mapping

### 6. `deye_solarman.py`

Handles communication with **Deye inverters** via **Solarman data logger**:

- Inherits from `Battery`

- Uses `pysolarmanv5` for communication

- Similar functionality to `deye_modbus.py` but using the Solarman API

### 7. `sessy.py`

Handles communication with **Sessy Battery System**:

- Uses `aiohttp` for asynchronous API communication with the Sessy API

- Supports reading active power, battery SOC, and grid voltage

- Allows setting power and current setpoints

### 8. `sma.py`

Handles communication with **SMA inverters**:

- Inherits from `ModbusBattery`

- Supports reading active power, battery SOC, and grid voltage

- Allows setting power and current setpoints

- Implements comprehensive register mapping


## Implementing a New Battery

To implement a new battery, follow these steps:

1. **Define the Battery Class**: Create a new class that inherits from the `Battery` or `ModbusBattery` class, depending on the communication protocol used by the new battery system.

2. **Initialize the Battery**: Implement the `__init__` method to initialize the battery-specific parameters and call the superclass constructor.

3. **Register Mapping**: If using Modbus communication, define the register mapping for the new battery system. You can use an Enum class to map the register addresses with their respective parameters, or you can use a dictionary or any other suitable data structure that fits your needs.

4. **Implement Required Methods**: Define methods to read and write battery parameters such as active power, state of charge (SOC), and grid voltage. Use the provided templates as a guide.

### Example Battery Implementation

```python
from battery import Battery

class MyNewBattery(Battery):
    def __init__(
        self, 
        capacity: int = None, 
        max_charge_power: int = None, 
        max_discharge_power: int = None, 
        soc: int = None
    ):
        super().__init__(capacity, max_charge_power, max_discharge_power, soc)
        # Initialize battery-specific parameters here

    def get_active_power_total(self):
        # Implement logic to get active power total
        pass

    def get_battery_soc(self):
        # Implement logic to get battery SOC
        pass

    def get_phase_voltage(self):
        # Implement logic to get grid voltage
        pass

    def set_power_setpoint(self, setpoint: int):
        # Implement logic to set power setpoint
        pass
```

### Example Modbus Battery Implementation

```python
from enum import Enum
from battery import ModbusBattery
from modbus import Register, AccessType, DataType

class MyNewModbusBattery(ModbusBattery):
    def __init__(
        self, 
        ip: str, 
        port: int = 502, 
        timeout: int = 3, 
        capacity: int = None, 
        max_charge_power: int = None, 
        max_discharge_power: int = None, 
        soc: int = None
    ):
        super().__init__(ip, port, timeout, capacity, max_charge_power, max_discharge_power, soc)

    def get_active_power(self):
        return self.read_holding_register(self.NewBatteryRegisters.active_power_total.value)

    def get_battery_soc(self):
        return self.read_holding_register(self.NewBatteryRegisters.battery_soc.value)

    def get_phase_voltage(self):
        return self.read_holding_register(self.NewBatteryRegisters.grid_voltage.value)

    def set_power_setpoint(self, setpoint: int):
        self.write_register(self.NewBatteryRegisters.power_setpoint.value, setpoint)

    class NewBatteryRegisters(Enum):
        grid_voltage = Register(30000, "grid_voltage", DataType.UINT16)
        battery_soc = Register(30001, "battery_soc", DataType.UINT16, gain=0.01)
        active_power_total = Register(30002, "active_power_total", DataType.UINT16, gain=10)
        power_setpoint = Register(30003, "power_setpoint", DataType.INT16, access_type=AccessType.READ_WRITE)
```

## References

- [Modbus Protocol Specification](https://modbus.org/specs.php)
- [Victron Energy Documentation](https://www.victronenergy.com/live/ccgx:modbustcp_faq)
- [Huawei SUN2000 Modbus Registers](https://www.debacher.de/wiki/Sun2000_Modbus_Register)
- [Deye Inverter Documentation](https://library.loxone.com/detail/deye-sun-12-inverter-1640/overview)
- [Sessy Battery System API](https://www.sessy.nl/wp-content/uploads/2024/07/api_docs_dongle.txt)
- [Solarman Data Logger](https://www.solarmanpv.com/products/data-logger/stick-logger/)
- [pysolarmanv5 Library](https://pypi.org/project/pysolarmanv5/)
- [SMA documentation](https://www.sma.de/en/service/downloads)
