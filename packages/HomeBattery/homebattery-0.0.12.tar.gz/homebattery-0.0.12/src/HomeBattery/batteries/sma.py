'''
SMA Inverter module
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

This module defines the SmaInverter class, which represents a battery system
with various functionalities such as retrieving power status, state of charge
(SOC), and grid voltage. It also allows setting the power setpoint and current
setpoint of the inverter. The SmaInverter class inherits from the ModbusBattery
class and uses the Modbus protocol to interact with the inverter.

'''

from ..battery import ModbusBattery
from ..modbus import Register, DataType, AccessType
from enum import Enum


class SmaInverter(ModbusBattery):
    '''Sma inverter class

    Arguments:
        ip (str): the ip address of the victron inverter
        port (int): the port of the victron inverter
        timeout (int): the timeout of the modbus client in seconds
        capacity (int): the capacity of the battery in Wh
        max_charge_power (int): the maximum charge power of the battery in W
        max_discharge_power (int): the maximum discharge power of the battery
                                   in W
        soc (int): the state of charge of the battery in %
    '''

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
        super().__init__(ip, port, timeout, capacity, max_charge_power,
                         max_discharge_power, soc)
        # Set the power control to 0x0322 to enable active power control
        self.write_register(self.SmaRegisters.power_control.value, 0x0322, 3)

    def set_power_setpoint(self, setpoint: int):
        '''Set the power setpoint of the inverter

        Arguments:
            setpoint (int): the power setpoint in W
        '''
        self.write_register(
            self.SmaRegisters.active_power_setpoint.value, setpoint, 3)

    def set_current_setpoint(self, setpoint: int):
        '''Set the current setpoint of the inverter

        Arguments:
            setpoint (int): the current setpoint in A
        '''
        phase_voltage = self.get_phase_voltage(1)
        power_setpoint = int(setpoint * phase_voltage)
        self.set_power_setpoint(power_setpoint)

    def get_active_power_total(self):
        '''Get the total active power of the inverter in W
        '''
        return self.read_holding_register(
            self.SmaRegisters.active_power.value, 3)

    def get_active_current_total(self):
        '''Get the total active current of the inverter in A
        '''
        return self.get_active_power_total() / self.get_phase_voltage(1)

    def get_battery_soc(self):
        '''Get the state of charge of the battery
        '''
        return self.read_holding_register(
            self.SmaRegisters.battery_soc.value, 3)

    def get_phase_voltage(self, phase: int):
        '''Get the grid voltage of the inverter in V

        Arguments:
            phase (int): the phase number
        '''
        if phase == 1:
            return self.read_holding_register(
                self.SmaRegisters.grid_voltage_l1.value, 3)
        elif phase == 2:
            return self.read_holding_register(
                self.SmaRegisters.grid_voltage_l2.value, 3)
        elif phase == 3:
            return self.read_holding_register(
                self.SmaRegisters.grid_voltage_l3.value, 3)
        else:
            raise ValueError("Invalid phase number")

    def get_grid_current(self, phase: int):
        '''Get the grid current of the inverter in A

        Arguments:
            phase (int): the phase number
        '''
        if phase == 1:
            return self.read_holding_register(
                self.SmaRegisters.grid_current_l1.value, 3)
        elif phase == 2:
            return self.read_holding_register(
                self.SmaRegisters.grid_current_l2.value, 3)
        elif phase == 3:
            return self.read_holding_register(
                self.SmaRegisters.grid_current_l3.value, 3)
        else:
            raise ValueError("Invalid phase number")

    class SmaRegisters(Enum):
        active_power_setpoint = Register(
            40149, "active_power_setpoint", DataType.INT32,
            count=2, access_type=AccessType.WRITE)
        power_control = Register(
            40151, "power_control", DataType.UINT32,
            count=2, access_type=AccessType.WRITE)
        operating_mode_power_setpoint = Register(
            40210, "operating_mode_power_setpoint", DataType.UINT32,
            count=2, access_type=AccessType.READ_WRITE)
        battery_soc = Register(
            30845, "battery_soc", DataType.UINT32, count=2)
        active_power = Register(
            30775, "active_power", DataType.INT32, count=2)
        battery_current = Register(
            30843, "battery_current", DataType.INT32, count=2, gain=1000)
        battery_temperature = Register(
            30849, "battery_temperature", DataType.UINT32, count=2, gain=10)
        battery_voltage = Register(
            30851, "battery_voltage", DataType.UINT32, count=2, gain=100)
        operating_status = Register(
            33003, "operating_status", DataType.UINT32, count=2)
        grid_voltage_l1 = Register(
            30783, "grid_voltage_l1", DataType.UINT32, count=2, gain=100)
        grid_voltage_l2 = Register(
            30785, "grid_voltage_l2", DataType.UINT32, count=2, gain=100)
        grid_voltage_l3 = Register(
            30787, "grid_voltage_l3", DataType.UINT32, count=2, gain=100)
        grid_current_l1 = Register(
            30977, "grid_current_l1", DataType.INT32, count=2, gain=1000)
        grid_current_l2 = Register(
            30979, "grid_current_l2", DataType.INT32, count=2, gain=1000)
        grid_current_l3 = Register(
            30981, "grid_current_l3", DataType.INT32, count=2, gain=1000)
