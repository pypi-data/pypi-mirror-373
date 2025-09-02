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
'''
from .modbus import ModbusDevice


class Battery:
    '''Base battery class

    Arguments:
        capacity (int): the capacity of the battery in Wh
        max_charge_power (int): the maximum charge power of the battery in W
        max_discharge_power (int): the maximum discharge power of the battery
                                   in W
        soc (int): the state of charge of the battery in %
    '''

    def __init__(
            self,
            capacity: int = None,
            max_charge_power: int = None,
            max_discharge_power: int = None,
            soc: int = None
    ):
        self._capacity = capacity
        self._max_charge_power = max_charge_power
        self._max_discharge_power = max_discharge_power
        self._soc = soc
        self._client = None

    def set_power_setpoint(self, setpoint: int):
        raise NotImplementedError("Not implemented")

    def set_current_setpoint(self, setpoint: int):
        raise NotImplementedError("Not implemented")

    def set_power_setpoint_phase(self, setpoint: int, phase: int):
        raise NotImplementedError("Not implemented")

    def set_current_setpoint_phase(self, setpoint: int, phase: int):
        raise NotImplementedError("Not implemented")

    def get_active_power_total(self):
        raise NotImplementedError("Not implemented")

    def get_active_current_total(self):
        raise NotImplementedError("Not implemented")

    def get_active_power_phase(self, phase: int):
        raise NotImplementedError("Not implemented")

    def get_active_current_phase(self, phase: int):
        raise NotImplementedError("Not implemented")

    def get_phase_voltage(self, phase: int):
        raise NotImplementedError("Not implemented")

    def get_battery_soc(self):
        raise NotImplementedError("Not implemented")


class ModbusBattery(Battery, ModbusDevice):
    '''Modbus battery class

    Arguments:
        modbus_ip (str): the ip address of the modbus battery
        modbus_port (int): the port of the modbus battery
        timeout (int): the timeout of the modbus battery in seconds
        capacity (int): the capacity of the battery in Wh
        max_charge_power (int): the maximum charge power of the battery in W
        max_discharge_power (int): the maximum discharge power of the battery
                                   in W
        soc (int): the state of charge of the battery in %
    '''

    def __init__(
            self,
            modbus_ip: str,
            modbus_port: int = 502,
            timeout: int = 3,
            capacity: int = None,
            max_charge_power: int = None,
            max_discharge_power: int = None,
            soc: int = None
    ):
        Battery.__init__(
            self,
            capacity,
            max_charge_power,
            max_discharge_power,
            soc
        )
        ModbusDevice.__init__(
            self,
            modbus_ip,
            modbus_port,
            timeout
        )
