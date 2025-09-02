'''
Copyright (C) 2025  ElaadNL

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

-------------------------------------------------------------------------------

This module provides a class to interface with a Deye inverter using Modbus
protocol. The DeyeInverter class allows for communication with the inverter
to read and write various parameters, such as power setpoints, battery state
of charge, and grid voltage.

The class utilizes the Battery base class and defines specific registers for
the Deye inverter. It includes methods to set power and current setpoints,
read all registers, and get specific values like active power and battery SOC.

The communication with the inverter is facilitated through the Solarman data
logger (LSW-3) using the pysolarmanv5 library. The pysolarmanv5 library
provides a Python interface to interact with Solarman data loggers, enabling
Modbus communication with the connected devices.
'''

import warnings
from enum import Enum
from ..battery import Battery
from ..modbus import Register, AccessType
from pysolarmanv5 import PySolarmanV5

# Inverter constants
CURRENT_LIMIT = 195


class DeyeSolarmanInverter(Battery):
    '''Deye solarman inverter class
    this class is used to communicate with a Deye inverter through the
    solarman data logger(LSW-3) making use of the pysolarmanv5 library

    Arguments:
        data_logger_ip (str): the ip address of the solarman data logger
        data_logger_port (int): the port of the solarman data logger
        data_logger_sn (int): the serial number of the solarman data logger
        manual_mode (bool): whether or not to use manual mode to set the power
                            setpoint
        capacity (int): the capacity of the battery
        max_charge_power (int): the maximum charge power of the battery in W
        max_discharge_power (int): the maximum discharge power of the battery
                                   in W
        soc (int): the state of charge of the battery in %
    '''

    def __init__(
            self,
            data_logger_ip: str,
            data_logger_port: int,
            data_logger_sn: int,
            manual_mode: int = True,
            capacity: int = None,
            max_charge_power: int = None,
            max_discharge_power: int = None,
            soc: int = None
    ):
        super().__init__(capacity, max_charge_power, max_discharge_power, soc)
        self._data_logger_ip = data_logger_ip
        self._data_logger_port = data_logger_port
        self._data_logger_sn = data_logger_sn
        self._client = PySolarmanV5(
            data_logger_ip, data_logger_sn, port=data_logger_port,
            mb_slave_id=1)

        self._manual_mode = manual_mode
        if manual_mode:
            self._init_power_setpoint_registers()

    def _set_discharge_setpoint(self, setpoint: int):
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellModeKWPoint6.value.address, (setpoint,))
        # Set SOC setpoint to 5 to discharge
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellModeBattCapacity6.value.address, (5,))

    def _set_charge_setpoint(self, setpoint: int):
        voltage = self.HoldingRegisters.BatteryVoltage.value.decode(
            self._client.read_holding_registers(
                self.HoldingRegisters.BatteryVoltage.value.address, 1))

        # TODO:: voltage changes slightly when charging so this is not
        # accurate, try using grid power limit register instead
        max_charge_current = int(setpoint / voltage)
        if max_charge_current > CURRENT_LIMIT:
            max_charge_current = CURRENT_LIMIT

        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.MaxChargeCurrent.value.address,
            (max_charge_current,))
        # Set SOC setpoint to 100 to charge
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellModeBattCapacity6.value.address, (100,))

    def _update_charge_current(self, setpoint: int):
        voltage = self.HoldingRegisters.BatteryVoltage.value.decode(
            self._client.read_holding_registers(
                self.HoldingRegisters.BatteryVoltage.value.address, 1))

        max_charge_current = int(setpoint / voltage)
        print(max_charge_current)

        if max_charge_current > CURRENT_LIMIT:
            max_charge_current = CURRENT_LIMIT

        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.MaxChargeCurrent.value.address,
            (max_charge_current,))

    def _init_power_setpoint_registers(self):
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.TimeOfUse.value.address, (0x00FF,))

        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellTimePoint1.value.address, (100,))
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellTimePoint2.value.address, (100,))
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellTimePoint3.value.address, (100,))
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellTimePoint4.value.address, (100,))
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellTimePoint5.value.address, (100,))
        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.SellTimePoint6.value.address, (100,))

        # with all time frames set to the same time, the inverter will always
        # use the settings from the sixth time frame so we only need to update
        # the settings in the sixth time frame to change the power setpoint

        self._client.write_multiple_holding_registers(
            self.HoldingRegisters.ChargeModeEnable6.value.address, (1,))

    def set_power_setpoint(self, setpoint: int):
        '''Sets the power setpoint of the inverter

        Arguments:
            setpoint (int): the power setpoint to set in W
        '''
        if (self._max_charge_power is None or
                self._max_discharge_power is None):
            warnings.warn("Max charge power or max discharge power not set, \
                          setpoint may exceed limits")
        elif setpoint > self._max_charge_power:
            warnings.warn(f"Power setpoint {setpoint} exceeds the maximum \
                          charge power {self._max_charge_power} \n\
                          Reverting to maximum charge power")
            setpoint = self._max_charge_power
        elif setpoint < -self._max_discharge_power:
            warnings.warn(f"Power setpoint {setpoint} exceeds the maximum \
                          discharge power {-self._max_discharge_power} \n\
                          Reverting to maximum discharge power")
            setpoint = -self._max_discharge_power

        if setpoint > 0:
            self._set_charge_setpoint(setpoint)
        else:
            self._set_discharge_setpoint(abs(setpoint))

    def set_current_setpoint(self, setpoint: int):
        '''Sets the current setpoint of the inverter

        Arguments:
            setpoint (int): the current setpoint to set in A
        '''
        phase_voltage = self.get_phase_voltage(1)
        power_setpoint = setpoint * phase_voltage
        self.set_power_setpoint(power_setpoint)

    def read_register(self, register: Register):
        '''Reads a specific register from the inverter and decodes the value

        Arguments:
            register_name (str): the name of the register to read

        Returns:
            float: the decoded value of the register
        '''
        return register.decode(
            self._client.read_holding_registers(register.address, 1))

    def read_all_registers(self):
        '''Reads all the holding registers from the inverter and decodes the
        values

        Returns:
            list: a list containing the name and the decoded value of each
                  register
        '''
        results = []
        for register in self.HoldingRegisters:
            if isinstance(register.value, Register):
                results.append([register.name, register.value.decode(
                    self._client.read_holding_registers(
                        register.value.address, 1))])
        return results

    def get_active_power_total(self):
        '''Gets the active power of the inverter

        Returns:
            float: the active power of the inverter in W
        '''
        return self.read_register(self.HoldingRegisters.ActivePower)

    def get_active_current_total(self):
        '''Gets the active total current of the inverter

        Returns:
            float: the active current of the inverter in A
        '''
        power = self.get_active_power_total()
        voltage = self.read_register(
            self.HoldingRegisters.GridphaseVoltageA.value, 1)

        return power / voltage

    def get_battery_soc(self):
        '''Gets the state of charge of the battery

        Returns:
            float: the state of charge of the battery
        '''
        return self.read_register(self.HoldingRegisters.BatterySOC)

    def get_phase_voltage(self, phase: int):
        '''Gets the grid voltage
        Arguments:
            phase (int): the phase to get the voltage from
        Returns:
            float: the grid voltage in V
        '''
        register = None
        if phase == 1:
            register = self.HoldingRegisters.GridphaseVoltageA.value
        elif phase == 2:
            register = self.HoldingRegisters.GridphaseVoltageB.value
        elif phase == 3:
            register = self.HoldingRegisters.GridphaseVoltageC.value
        if register:
            return self.read_register(register, 1)
        else:
            raise ValueError("Invalid phase")

    def disconnect(self):
        '''Disconnects the inverter'''
        self._client.disconnect()

    def connect(self):
        '''Connects to the inverter'''
        self._client = PySolarmanV5(
            self._data_logger_ip, self._data_logger_sn,
            port=self._data_logger_port, mb_slave_id=1)

    class HoldingRegisters(Enum):
        LimitControlFunction = Register(
            142, "LimitControlFunction", access_type=AccessType.READ_WRITE)
        LimitMaxGridPower = Register(
            143, "LimitMaxGridPower", unit="W",
            access_type=AccessType.READ_WRITE)
        TimeOfUse = Register(
            146, "TimeOfUse", access_type=AccessType.READ_WRITE)

        # Starting time for each time frame
        SellTimePoint1 = Register(
            148, "SellTimePoint1", unit="hh:mm",
            access_type=AccessType.READ_WRITE)
        SellTimePoint2 = Register(
            149, "SellTimePoint2", unit="hh:mm",
            access_type=AccessType.READ_WRITE)
        SellTimePoint3 = Register(
            150, "SellTimePoint3", unit="hh:mm",
            access_type=AccessType.READ_WRITE)
        SellTimePoint4 = Register(
            151, "SellTimePoint4", unit="hh:mm",
            access_type=AccessType.READ_WRITE)
        SellTimePoint5 = Register(
            152, "SellTimePoint5", unit="hh:mm",
            access_type=AccessType.READ_WRITE)
        SellTimePoint6 = Register(
            153, "SellTimePoint6", unit="hh:mm",
            access_type=AccessType.READ_WRITE)

        # Discharge power setpoint
        SellModeKWPoint1 = Register(
            154, "SellModeKWPoint1", unit="W",
            access_type=AccessType.READ_WRITE)
        SellModeKWPoint2 = Register(
            155, "SellModeKWPoint2", unit="W",
            access_type=AccessType.READ_WRITE)
        SellModeKWPoint3 = Register(
            156, "SellModeKWPoint3", unit="W",
            access_type=AccessType.READ_WRITE)
        SellModeKWPoint4 = Register(
            157, "SellModeKWPoint4", unit="W",
            access_type=AccessType.READ_WRITE)
        SellModeKWPoint5 = Register(
            158, "SellModeKWPoint5", unit="W",
            access_type=AccessType.READ_WRITE)
        SellModeKWPoint6 = Register(
            159, "SellModeKWPoint6", unit="W",
            access_type=AccessType.READ_WRITE)

        # Battery voltage setpoint can be used instead of SOC setpoint
        SellModeBattVolt1 = Register(
            160, "SellModeBattVolt1", unit="V",
            access_type=AccessType.READ_WRITE)
        SellModeBattVolt2 = Register(
            161, "SellModeBattVolt2", unit="V",
            access_type=AccessType.READ_WRITE)
        SellModeBattVolt3 = Register(
            162, "SellModeBattVolt3", unit="V",
            access_type=AccessType.READ_WRITE)
        SellModeBattVolt4 = Register(
            163, "SellModeBattVolt4", unit="V",
            access_type=AccessType.READ_WRITE)
        SellModeBattVolt5 = Register(
            164, "SellModeBattVolt5", unit="V",
            access_type=AccessType.READ_WRITE)
        SellModeBattVolt6 = Register(
            165, "SellModeBattVolt6", unit="V",
            access_type=AccessType.READ_WRITE)

        # SOC setpoint
        SellModeBattCapacity1 = Register(
            166, "SellModeBattCapacity1", unit="%",
            access_type=AccessType.READ_WRITE)
        SellModeBattCapacity2 = Register(
            167, "SellModeBattCapacity2", unit="%",
            access_type=AccessType.READ_WRITE)
        SellModeBattCapacity3 = Register(
            168, "SellModeBattCapacity3", unit="%",
            access_type=AccessType.READ_WRITE)
        SellModeBattCapacity4 = Register(
            169, "SellModeBattCapacity4", unit="%",
            access_type=AccessType.READ_WRITE)
        SellModeBattCapacity5 = Register(
            170, "SellModeBattCapacity5", unit="%",
            access_type=AccessType.READ_WRITE)
        SellModeBattCapacity6 = Register(
            171, "SellModeBattCapacity6", unit="%",
            access_type=AccessType.READ_WRITE)

        # Enable/disable whether or not to allow charging the battery from the
        # grid
        ChargeModeEnable1 = Register(
            172, "ChargeModeEnable1", access_type=AccessType.READ_WRITE)
        ChargeModeEnable2 = Register(
            173, "ChargeModeEnable2", access_type=AccessType.READ_WRITE)
        ChargeModeEnable3 = Register(
            174, "ChargeModeEnable3", access_type=AccessType.READ_WRITE)
        ChargeModeEnable4 = Register(
            175, "ChargeModeEnable4", access_type=AccessType.READ_WRITE)
        ChargeModeEnable5 = Register(
            176, "ChargeModeEnable5", access_type=AccessType.READ_WRITE)
        ChargeModeEnable6 = Register(
            177, "ChargeModeEnable6", access_type=AccessType.READ_WRITE)

        MaxChargeCurrent = Register(
            108, "MaxChargeCurrent", unit="A",
            access_type=AccessType.READ_WRITE)
        MaxDischargeCurrent = Register(
            109, "MaxDischargeCurrent", unit="A",
            access_type=AccessType.READ_WRITE)

        BatterySOC = Register(
            214, "BatterySOC", unit="%", access_type=AccessType.READ)
        BatteryVoltage = Register(
            215, "BatteryVoltage", gain=100, unit="V",
            access_type=AccessType.READ)

        BatteryOutputCurrent = Register(
            591, "BatteryOutputCurrent", gain=100, unit="A",
            access_type=AccessType.READ)
        GridphaseVoltageA = Register(
            598, "GridphaseVoltageA", gain=10, unit="V",
            access_type=AccessType.READ)
        GridphaseVoltageB = Register(
            599, "GridphaseVoltageB", gain=10, unit="V",
            access_type=AccessType.READ)
        GridphaseVoltageC = Register(
            600, "GridphaseVoltageC", gain=10, unit="V",
            access_type=AccessType.READ)

        ActivePower = Register(
            607, "ActivePower", unit="W", access_type=AccessType.READ)

        GridSideInnerCurrentA = Register(
            610, "GridSideInnerCurrentA", gain=100, unit="A",
            access_type=AccessType.READ)
        GridSideInnerCurrentB = Register(
            611, "GridSideInnerCurrentB", gain=100, unit="A",
            access_type=AccessType.READ)
        GridSideInnerCurrentC = Register(
            612, "GridSideInnerCurrentC", gain=100, unit="A",
            access_type=AccessType.READ)
        OutOfGridCurrentA = Register(
            613, "OutOfGridCurrentA", gain=100, unit="A",
            access_type=AccessType.READ)
        OutOfGridCurrentB = Register(
            614, "OutOfGridCurrentB", gain=100, unit="A",
            access_type=AccessType.READ)
        OutOfGridCurrentC = Register(
            615, "OutOfGridCurrentC", gain=100, unit="A",
            access_type=AccessType.READ)

        InverterOutputCurrentA = Register(
            630, "InverterOutputCurrentA", gain=100, unit="A",
            access_type=AccessType.READ)
        InverterOutputCurrentB = Register(
            631, "InverterOutputCurrentB", gain=100, unit="A",
            access_type=AccessType.READ)
        InverterOutputCurrentC = Register(
            632, "InverterOutputCurrentC", gain=100, unit="A",
            access_type=AccessType.READ)
