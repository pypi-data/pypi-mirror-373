"""
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

This module defines the Sessy class, which represents a battery system with
various functionalities such as retrieving power status, phase voltage, state
of charge (SOC), power, energy status, and active strategy. It also allows
setting the active strategy and sending power or current setpoints to the
battery system. The Sessy class inherits from the Battery class and uses
aiohttp for asynchronous HTTP requests to interact with the battery system's
API.
"""

import warnings
from ..battery import Battery
from aiohttp import BasicAuth, ClientSession, ClientConnectionError, \
    ClientResponseError, ContentTypeError
from aiohttp.client_exceptions import InvalidURL
from aiohttp import ClientTimeout
from enum import Enum


class PowerStrategy(Enum):
    NOM = "POWER_STRATEGY_NOM"
    ROI = "POWER_STRATEGY_ROI"
    API = "POWER_STRATEGY_API"
    IDLE = "POWER_STRATEGY_IDLE"
    SESSY_CONNECT = "POWER_STRATEGY_SESSY_CONNECT"
    ECO = "POWER_STRATEGY_ECO"


class SessyInverter(Battery):
    '''Sessy inverter class

    Arguments:
        ip (str): the ip address of the Sessy battery
        username (str): the username for the Sessy battery
        password (str): the password for the Sessy battery
        capacity (int): the capacity of the battery in Wh
        max_charge_power (int): the maximum charge power of the battery in W
        max_discharge_power (int): the maximum discharge power of the battery
                                   in W
        soc (int): the state of charge of the battery in %
    '''

    def __init__(
            self,
            ip: str,
            username: str,
            password: str,
            capacity: int = None,
            max_charge_power: int = None,
            max_discharge_power: int = None,
            soc: int = None
    ):
        super().__init__(capacity, max_charge_power, max_discharge_power, soc)
        self._ip = ip
        self._soc = soc
        self._power = None
        self._voltage = {"phase1": None, "phase2": None,
                         "phase3": None, "total": None}
        self._current = {"phase1": None, "phase2": None,
                         "phase3": None, "total": None}
        self._url = f"http://{self._ip}/api/v1"
        self._username = username
        self._password = password
        self._client = ClientSession(
            auth=BasicAuth(self._username, self._password),
            timeout=ClientTimeout(total=60),
            raise_for_status=True
        )

    async def _get_power_status(self):
        ''' Get the power status of the inverter'''
        endpoint = f"{self._url}/power/status"
        try:
            async with self._client.get(endpoint) as response:
                data = await response.json()
                sessy_data = data.get('sessy')
                if sessy_data:
                    self._soc = sessy_data.get('state_of_charge') * 100
                    self._power = sessy_data.get('power')
                return data
        except (ClientConnectionError, ClientResponseError,
                ContentTypeError, InvalidURL) as e:
            print(f"Error retrieving power status: {e}")
            raise

    async def _get_phase_data(self, phase: int):
        ''' Get the phase data of the inverter'''
        endpoint = f"{self._url}/power/status"
        try:
            async with self._client.get(endpoint) as response:
                data = await response.json()
                phase_data = data.get(f"renewable_energy_phase{phase}")
                if phase_data:
                    phase_voltage = phase_data.get('voltage_rms')
                    phase_current = phase_data.get('current_rms')
                    self._voltage[f"phase{phase}"] = phase_voltage / 1000
                    self._current[f"phase{phase}"] = phase_current
        except (ClientConnectionError, ClientResponseError,
                ContentTypeError, InvalidURL) as e:
            print(f"Error retrieving power status: {e}")
            raise

    async def get_phase_voltage(self, phase: int):
        ''' Get the voltage of a specific phase of the inverter in V'''
        if phase not in [1, 2, 3]:
            raise ValueError("Invalid phase input, must be 1, 2 or 3")

        await self._get_phase_data(phase)
        return self._voltage[f"phase{phase}"]

    async def get_phase_current(self, phase: int):
        ''' Get the active current of a specific phase of the inverter in A'''
        if phase not in [1, 2, 3]:
            raise ValueError("Invalid phase input, must be 1, 2 or 3")

        await self._get_phase_data(phase)
        return self._current[f"phase{phase}"]

    async def get_battery_soc(self):
        ''' Get the state of charge of the battery'''
        await self._get_power_status()
        return self._soc

    async def get_active_power_total(self):
        ''' Get the total active power of the inverter in W'''
        await self._get_power_status()
        return self._power

    async def get_active_current_total(self):
        ''' Get the total active current of the inverter in A'''
        await self._get_power_status()
        self._current["total"] = \
            self._power / await self.get_phase_voltage(phase=1)
        return self._current["total"]

    async def get_active_strategy(self):
        ''' Get the active strategy of the inverter'''
        endpoint = f"{self._url}/power/active_strategy"
        try:
            async with self._client.get(endpoint) as response:
                return await response.json()
        except (ClientConnectionError, ClientResponseError,
                ContentTypeError, InvalidURL) as e:
            print(f"Error retrieving active strategy: {e}")
            raise

    async def set_active_strategy(self, strategy: PowerStrategy):
        ''' Set the active strategy of the battery system'''
        endpoint = f"{self._url}/power/active_strategy"
        payload = {"strategy": strategy.value}
        try:
            async with self._client.post(endpoint, json=payload) as response:
                if response.status == 200:
                    return True
        except (ClientConnectionError, ClientResponseError,
                ContentTypeError, InvalidURL) as e:
            print(f"Error setting active strategy: {e}")
            raise

    async def set_power_setpoint(self, setpoint: int):
        ''' Set the power setpoint of the battery system in W'''
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

        endpoint = f"{self._url}/power/setpoint"
        payload = {"setpoint": setpoint}
        try:
            async with self._client.post(endpoint, json=payload) as response:
                if response.status == 200:
                    return True
        except (ClientConnectionError, ClientResponseError,
                ContentTypeError, InvalidURL) as e:
            print(f"Error sending setpoint: {e}")
            raise

    async def set_current_setpoint(self, setpoint: int):
        ''' Set the current setpoint of the battery system in A'''
        phase_voltage = await self.get_phase_voltage(phase=1)
        power_setpoint = setpoint * phase_voltage
        return await self.set_power_setpoint(power_setpoint)
