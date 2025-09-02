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

This module provides a class to interact with Victron inverters via Modbus
protocol. It defines the `VictronInverter` class, which inherits from
`ModbusBattery` and includes methods to initialize power setpoint registers,
send power and current setpoints, and retrieve various metrics such as active
power, state of charge, and phase voltage. The module also defines several
enumerations for system, battery, Multiplus GX, VEbus, and grid registers,
which are used to map Modbus registers to meaningful names and data types.

NOTE:: Slave ID's can differ based on the system configuration. Figure out the
correct slave ID's for your system by looking at the Modbus register map
provided by Victron.
'''

import warnings
from enum import Enum
from ..battery import ModbusBattery
from ..modbus import Register, AccessType, DataType


class VictronInverter(ModbusBattery):
    '''Victron inverter class

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

        self.init_power_setpoint_registers()

    def init_power_setpoint_registers(self):
        '''Initialize power setpoint registers of the victron inverter
        Ensures that the disable charge and feedback flags are set to 0
        and the ess mode is set to 3 for external control
        '''
        self.write_register(
            self.VEbusRegisters.ess_disable_charge_flag_phase.value,
            0,  # 0 to enable charging
            self.VEbusRegisters.slave_id.value
        )
        self.write_register(
            self.VEbusRegisters.ess_disable_feedback_flag_phase.value,
            0,  # 0 to enable feedback
            self.VEbusRegisters.slave_id.value
        )
        self.write_register(
            self.SystemRegisters.ess_mode.value,
            3,  # 3 for external control
            self.SystemRegisters.slave_id.value
        )

    def set_power_setpoint_phase(self, setpoint: int, phase: int):
        '''Send the power setpoint to the victron inverter

        Arguments:
            setpoint (int): the setpoint to send in W
            phase (int): the phase to send the setpoint to
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

        register = None
        if phase == 1:
            register = self.VEbusRegisters.ess_power_setpoint_phase_1.value
        elif phase == 2:
            register = self.VEbusRegisters.ess_power_setpoint_phase_2.value
        elif phase == 3:
            register = self.VEbusRegisters.ess_power_setpoint_phase_3.value
        if register:
            self.write_register(
                register,
                setpoint,
                self.VEbusRegisters.slave_id.value
            )
        else:
            raise ValueError("Invalid phase")

    def set_current_setpoint_phase(self, setpoint: int, phase: int):
        '''Send the current setpoint to the victron inverter

        Arguments:
            setpoint (int): the setpoint to send in A
            phase (int): the phase to send the setpoint to
        '''
        phase_voltage = self.get_phase_voltage(phase)
        power_setpoint = int(setpoint * phase_voltage)
        self.set_power_setpoint_phase(power_setpoint, phase)

    def set_power_setpoint(self, setpoint: int):
        '''Send the power setpoint to the victron inverter on phase 1

        Arguments:
            setpoint (int): the setpoint to send in W
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

        register = self.VEbusRegisters.ess_power_setpoint_phase_1.value
        self.write_register(
            register,
            setpoint,
            self.VEbusRegisters.slave_id.value
        )

    def set_current_setpoint(self, setpoint: int):
        '''Send the current setpoint to the victron inverter on phase 1

        Arguments:
            setpoint (int): the setpoint to send in A
        '''
        phase_voltage = self.get_phase_voltage(1)
        power_setpoint = int(setpoint * phase_voltage)
        self.set_power_setpoint_phase(power_setpoint, 1)

    def get_active_power_total(self):
        '''Get the total active power of the victron inverter

        Returns:
            int: the active power of the victron inverter in W
        '''
        return self.read_holding_register(
            self.SystemRegisters.vebus_charge_power_system.value,
            self.SystemRegisters.slave_id.value
        )

    def get_active_current_total(self):
        '''Get the total active current of the victron inverter

        Returns:
            int: the active current of the victron inverter in A
        '''
        return self.read_holding_register(
            self.SystemRegisters.vebus_charge_current_system.value,
            self.SystemRegisters.slave_id.value
        )

    def get_battery_soc(self):
        '''Get the state of charge of the battery

        Returns:
            int: the state of charge of the battery
        '''
        return self.read_holding_register(
            self.BatteryRegisters.state_of_charge.value,
            self.BatteryRegisters.slave_id.value
        )

    def get_phase_voltage(self, phase: int):
        '''Get the voltage of a specific phase

        Arguments:
            phase (int): the phase to get the voltage of

        Returns:
            int: the voltage of the phase in V
        '''
        register = None
        if phase == 1:
            register = self.VEbusRegisters.input_voltage_phase_1.value
        elif phase == 2:
            register = self.VEbusRegisters.input_voltage_phase_2.value
        elif phase == 3:
            register = self.VEbusRegisters.input_voltage_phase_3.value
        if register:
            return self.read_holding_register(
                register,
                self.VEbusRegisters.slave_id.value
            )
        else:
            raise ValueError("Invalid phase")

    def get_phase_current(self, phase: int):
        '''Get the current of a specific phase

        Arguments:
            phase (int): the phase to get the current of

        Returns:
            int: the current of the phase in A
        '''
        register = None
        if phase == 1:
            register = self.VEbusRegisters.input_current_phase_1.value
        elif phase == 2:
            register = self.VEbusRegisters.input_current_phase_2.value
        elif phase == 3:
            register = self.VEbusRegisters.input_current_phase_3.value
        if register:
            return self.read_holding_register(
                register,
                self.VEbusRegisters.slave_id.value
            )
        else:
            raise ValueError("Invalid phase")

    class SystemRegisters(Enum):
        slave_id = 100
        serial_system = Register(
            800, "serial system", DataType.STRING, count=6)
        ccgx_relay_1_state = Register(
            806, "ccgx relay 1 state", DataType.UINT16)
        ccgx_rSlay_2_state = Register(
            807, "ccgx relay 2 state", DataType.UINT16)
        pv_ac_coupled_on_output_l1 = Register(
            808, "pv ac coupled on output l1", DataType.UINT16)
        pv_ac_coupled_on_output_l2 = Register(
            809, "pv ac coupled on output l2", DataType.UINT16)
        pv_ac_coupled_on_output_l3 = Register(
            810, "pv ac coupled on output l3", DataType.UINT16)
        pv_ac_coupled_on_input_l1 = Register(
            811, "pv ac coupled on input l1", DataType.UINT16)
        pv_ac_coupled_on_input_l2 = Register(
            812, "pv ac coupled on input l2", DataType.UINT16)
        pv_ac_coupled_on_input_l3 = Register(
            813, "pv ac coupled on input l3", DataType.UINT16)
        pv_ac_coupled_on_generator_l1 = Register(
            814, "pv ac coupled on generator l1", DataType.UINT16)
        pv_ac_coupled_on_generator_l2 = Register(
            815, "pv ac coupled on generator l2", DataType.UINT16)
        pv_ac_coupled_on_generator_l3 = Register(
            816, "pv ac coupled on generator l3", DataType.UINT16)
        ac_consumption_l1 = Register(817, "ac consumption l1", DataType.UINT16)
        ac_consumption_l2 = Register(818, "ac consumption l2", DataType.UINT16)
        ac_consumption_l3 = Register(819, "ac consumption l3", DataType.UINT16)
        grid_l1 = Register(820, "grid l1", DataType.INT16)
        grid_l2 = Register(821, "grid l2", DataType.INT16)
        grid_l3 = Register(822, "grid l3", DataType.INT16)
        genset_l1 = Register(823, "genset l1", DataType.INT16)
        genset_l2 = Register(824, "genset l2", DataType.INT16)
        genset_l3 = Register(825, "genset l3", DataType.INT16)
        active_input_source = Register(
            826, "active input source", DataType.UINT16)
        battery_voltage_system = Register(
            840, "battery voltage system", DataType.UINT16, gain=10)
        battery_current_system = Register(
            841, "battery current system", DataType.INT16, gain=10)
        battery_power_system = Register(
            842, "battery power system", DataType.INT16)
        battery_state_of_charge_system = Register(
            843, "battery state of charge system", DataType.UINT16)
        battery_state_system = Register(
            844, "battery state system", DataType.UINT16)
        battery_consumed_amphours_system = Register(
            845, "battery consumed amphours system", DataType.UINT16)
        battery_time_to_go_system = Register(
            846, "battery time to go system", DataType.UINT16)
        pv_dc_coupled_power = Register(
            850, "pv dc coupled power", DataType.UINT16)
        pv_dc_coupled_current = Register(
            851, "pv dc coupled current", DataType.INT16)
        charger_power = Register(855, "charger power", DataType.UINT16)
        dc_system_power = Register(860, "dc system power", DataType.INT16)
        vebus_charge_current_system = Register(
            865, "vebus charge current system", DataType.INT16, gain=10)
        vebus_charge_power_system = Register(
            866, "vebus charge power system", DataType.INT16)
        inverter_charger_current = Register(
            868, "inverter charger current", DataType.INT32, gain=10)
        inverter_charger_power = Register(
            870, "inverter charger power", DataType.INT32)
        ess_mode = Register(
            2902, "ess mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)

    class BatteryRegisters(Enum):
        slave_id = 225
        battery_power = Register(258, "battery power", DataType.INT16)
        battery_voltage = Register(
            259, "battery voltage", DataType.UINT16, gain=100)
        starter_battery_voltage = Register(
            260, "starter battery voltage", DataType.UINT16, gain=100)
        current = Register(261, "current", DataType.INT16, gain=10)
        battery_temperature = Register(
            262, "battery temperature", DataType.INT16, gain=10)
        mid_point_voltage_of_the_battery_bank = Register(
            263, "mid point voltage of the battery bank", DataType.UINT16,
            gain=100)
        mid_point_deviation_of_the_battery_bank = Register(
            264, "mid point deviation of the battery bank", DataType.UINT16,
            gain=100)
        consumed_amphours = Register(
            265, "consumed amphours", DataType.UINT16, gain=-0.1)
        state_of_charge = Register(
            266, "state of charge", DataType.UINT16, gain=10)
        alarm = Register(267, "alarm", DataType.UINT16)
        low_voltage_alarm = Register(268, "low voltage alarm", DataType.UINT16)
        high_voltage_alarm = Register(
            269, "high voltage alarm", DataType.UINT16)
        low_starter_voltage_alarm = Register(
            270, "low starter voltage alarm", DataType.UINT16)
        high_starter_voltage_alarm = Register(
            271, "high starter voltage alarm", DataType.UINT16)
        low_state_of_charge_alarm = Register(
            272, "low state of charge alarm", DataType.UINT16)
        low_temperature_alarm = Register(
            273, "low temperature alarm", DataType.UINT16)
        high_temperature_alarm = Register(
            274, "high temperature alarm", DataType.UINT16)
        mid_voltage_alarm = Register(275, "mid voltage alarm", DataType.UINT16)
        low_fused_voltage_alarm = Register(
            276, "low fused voltage alarm", DataType.UINT16)
        high_fused_voltage_alarm = Register(
            277, "high fused voltage alarm", DataType.UINT16)
        fuse_blown_alarm = Register(278, "fuse blown alarm", DataType.UINT16)
        high_internal_temperature_alarm = Register(
            279, "high internal temperature alarm", DataType.UINT16)
        relay_status = Register(280, "relay status", DataType.UINT16)
        deepest_discharge = Register(
            281, "deepest discharge", DataType.UINT16, gain=-0.1)
        last_discharge = Register(
            282, "last discharge", DataType.UINT16, gain=-0.1)
        average_discharge = Register(
            283, "average discharge", DataType.UINT16, gain=-0.1)
        charge_cycles = Register(284, "charge cycles", DataType.UINT16)
        full_discharges = Register(285, "full discharges", DataType.UINT16)
        total_ah_drawn = Register(
            286, "total ah drawn", DataType.UINT16, gain=-0.1)
        minimum_voltage = Register(
            287, "minimum voltage", DataType.UINT16, gain=100)
        maximum_voltage = Register(
            288, "maximum voltage", DataType.UINT16, gain=100)
        time_since_last_full_charge = Register(
            289, "time since last full charge", DataType.UINT16, gain=0.01)
        automatic_syncs = Register(290, "automatic syncs", DataType.UINT16)
        low_voltage_alarms = Register(
            291, "low voltage alarms", DataType.UINT16)
        high_voltage_alarms = Register(
            292, "high voltage alarms", DataType.UINT16)
        low_starter_voltage_alarms = Register(
            293, "low starter voltage alarms", DataType.UINT16)
        high_starter_voltage_alarms = Register(
            294, "high starter voltage alarms", DataType.UINT16)
        minimum_starter_voltage = Register(
            295, "minimum starter voltage", DataType.UINT16, gain=100)
        maximum_starter_voltage = Register(
            296, "maximum starter voltage", DataType.UINT16, gain=100)
        low_fused_voltage_alarms = Register(
            297, "low fused voltage alarms", DataType.UINT16)
        high_fused_voltage_alarms = Register(
            298, "high fused voltage alarms", DataType.UINT16)
        minimum_fused_voltage = Register(
            299, "minimum fused voltage", DataType.UINT16, gain=100)
        maximum_fused_voltage = Register(
            300, "maximum fused voltage", DataType.UINT16, gain=100)
        discharged_energy = Register(
            301, "discharged energy", DataType.UINT16, gain=10)
        charged_energy = Register(
            302, "charged energy", DataType.UINT16, gain=10)
        time_to_go = Register(303, "time to go", DataType.UINT16, gain=0.01)
        state_of_health = Register(
            304, "state of health", DataType.UINT16, gain=10)
        max_charge_voltage = Register(
            305, "max charge voltage", DataType.UINT16, gain=10)
        min_discharge_voltage = Register(
            306, "min discharge voltage", DataType.UINT16, gain=10)
        max_charge_current = Register(
            307, "max charge current", DataType.UINT16, gain=10)
        max_discharge_current = Register(
            308, "max discharge current", DataType.UINT16, gain=10)
        capacity = Register(309, "capacity", DataType.UINT16, gain=10)
        diagnostics_1st_last_error_timestamp = Register(
            310, "diagnostics 1st last error timestamp", DataType.UINT32)
        diagnostics_2nd_last_error_timestamp = Register(
            312, "diagnostics 2nd last error timestamp", DataType.UINT32)
        diagnostics_3rd_last_error_timestamp = Register(
            314, "diagnostics 3rd last error timestamp", DataType.UINT32)
        diagnostics_4th_last_error_timestamp = Register(
            316, "diagnostics 4th last error timestamp", DataType.UINT32)
        minimum_cell_temperature = Register(
            318, "minimum cell temperature", DataType.INT16, gain=10)
        maximum_cell_temperature = Register(
            319, "maximum cell temperature", DataType.INT16, gain=10)
        high_charge_current_alarm = Register(
            320, "high charge current alarm", DataType.UINT16)
        high_discharge_current_alarm = Register(
            321, "high discharge current alarm", DataType.UINT16)
        cell_imbalance_alarm = Register(
            322, "cell imbalance alarm", DataType.UINT16)
        internal_failure_alarm = Register(
            323, "internal failure alarm", DataType.UINT16)
        high_charge_temperature_alarm = Register(
            324, "high charge temperature alarm", DataType.UINT16)
        low_charge_temperature_alarm = Register(
            325, "low charge temperature alarm", DataType.UINT16)
        low_cell_voltage_alarm = Register(
            326, "low cell voltage alarm", DataType.UINT16)
        mode = Register(327, "mode", DataType.UINT16)
        state = Register(1282, "state", DataType.UINT16)
        error = Register(1283, "error", DataType.UINT16)
        system_switch = Register(1284, "system switch", DataType.UINT16)
        balancing = Register(1285, "balancing", DataType.UINT16)
        system_number_of_batteries = Register(
            1286, "system number of batteries", DataType.UINT16)
        system_batteries_parallel = Register(
            1287, "system batteries parallel", DataType.UINT16)
        system_batteries_series = Register(
            1288, "system batteries series", DataType.UINT16)
        system_number_of_cells_per_battery = Register(
            1289, "system number of cells per battery", DataType.UINT16)
        system_minimum_cell_voltage = Register(
            1290, "system minimum cell voltage", DataType.UINT16, gain=100)
        system_maximum_cell_voltage = Register(
            1291, "system maximum cell voltage", DataType.UINT16, gain=100)
        diagnostics_shutdowns_due_to_error = Register(
            1292, "diagnostics shutdowns due to error", DataType.UINT16)
        diagnostics_1st_last_error = Register(
            1293, "diagnostics 1st last error", DataType.UINT16)
        diagnostics_2nd_last_error = Register(
            1294, "diagnostics 2nd last error", DataType.UINT16)
        diagnostics_3rd_last_error = Register(
            1295, "diagnostics 3rd last error", DataType.UINT16)
        diagnostics_4th_last_error = Register(
            1296, "diagnostics 4th last error", DataType.UINT16)
        io_allow_to_charge = Register(
            1297, "io allow to charge", DataType.UINT16)
        io_allow_to_discharge = Register(
            1298, "io allow to discharge", DataType.UINT16)
        io_external_relay = Register(
            1299, "io external relay", DataType.UINT16)
        history_min_cell_voltage = Register(
            1300, "history min cell voltage", DataType.UINT16, gain=100)
        history_max_cell_voltage = Register(
            1301, "history max cell voltage", DataType.UINT16, gain=100)

    class MultiplusGXRegisters(Enum):
        slave_id = 230
        input_voltage_phase_1 = Register(
            4500, "input voltage phase 1", DataType.UINT16)
        input_voltage_phase_2 = Register(
            4501, "input voltage phase 2", DataType.UINT16)
        input_voltage_phase_3 = Register(
            4502, "input voltage phase 3", DataType.UINT16)
        input_current_phase_1 = Register(
            4503, "input current phase 1", DataType.UINT16)
        input_current_phase_2 = Register(
            4504, "input current phase 2", DataType.UINT16)
        input_current_phase_3 = Register(
            4505, "input current phase 3", DataType.UINT16)
        input_power_phase_1 = Register(
            4506, "input power phase 1", DataType.INT16)
        input_power_phase_2 = Register(
            4507, "input power phase 2", DataType.INT16)
        input_power_phase_3 = Register(
            4508, "input power phase 3", DataType.INT16)
        input_frequency = Register(4509, "input frequency", DataType.UINT16)
        output_voltage_phase_1 = Register(
            4510, "output voltage phase 1", DataType.UINT16)
        output_voltage_phase_2 = Register(
            4511, "output voltage phase 2", DataType.UINT16)
        output_voltage_phase_3 = Register(
            4512, "output voltage phase 3", DataType.UINT16)
        output_current_phase_1 = Register(
            4513, "output current phase 1", DataType.UINT16)
        output_current_phase_2 = Register(
            4514, "output current phase 2", DataType.UINT16)
        output_current_phase_3 = Register(
            4515, "output current phase 3", DataType.UINT16)
        output_power_phase_1 = Register(
            4516, "output power phase 1", DataType.INT16)
        output_power_phase_2 = Register(
            4517, "output power phase 2", DataType.INT16)
        output_power_phase_3 = Register(
            4518, "output power phase 3", DataType.INT16)
        output_frequency = Register(4519, "output frequency", DataType.UINT16)
        ac_input_1_source_type = Register(
            4520, "ac input 1 source type", DataType.UINT16)
        ac_input_2_source_type = Register(
            4521, "ac input 2 source type", DataType.UINT16)
        ac_input_1_current_limit = Register(
            4522, "ac input 1 current limit", DataType.UINT16)
        ac_input_2_current_limit = Register(
            4523, "ac input 2 current limit", DataType.UINT16)
        phase_count = Register(4524, "phase count", DataType.UINT16)
        active_ac_input = Register(4525, "active ac input", DataType.UINT16)
        battery_voltage = Register(4526, "battery voltage", DataType.UINT16)
        battery_current = Register(4527, "battery current", DataType.INT16)
        battery_temperature = Register(
            4528, "battery temperature", DataType.INT16)
        battery_state_of_charge = Register(
            4529, "battery state of charge", DataType.UINT16)
        inverter_state = Register(4530, "inverter state", DataType.UINT16)
        switch_position = Register(4531, "switch position", DataType.UINT16)
        temperature_alarm = Register(
            4532, "temperature alarm", DataType.UINT16)
        high_voltage_alarm = Register(
            4533, "high voltage alarm", DataType.UINT16)
        high_ac_out_voltage_alarm = Register(
            4534, "high ac out voltage alarm", DataType.UINT16)
        low_battery_temperature_alarm = Register(
            4535, "low battery temperature alarm", DataType.UINT16)
        low_voltage_alarm = Register(
            4536, "low voltage alarm", DataType.UINT16)
        low_ac_out_voltage_alarm = Register(
            4537, "low ac out voltage alarm", DataType.UINT16)
        overload_alarm = Register(4538, "overload alarm", DataType.UINT16)
        high_dc_ripple_alarm = Register(
            4539, "high dc ripple alarm", DataType.UINT16)
        pv_power = Register(4540, "pv power", DataType.UINT16)
        user_yield = Register(4541, "user yield", DataType.UINT16)
        relay_on_the_multi_rs = Register(
            4542, "relay on the multi rs", DataType.UINT16)
        mpp_operation_mode = Register(
            4543, "mpp operation mode", DataType.UINT16)
        pv_voltage = Register(4544, "pv voltage", DataType.UINT16)
        error_code = Register(4545, "error code", DataType.UINT16)
        energy_from_ac_in_1_to_ac_out = Register(
            4546, "energy from ac in 1 to ac out", DataType.UINT32)
        energy_from_ac_in_1_to_battery = Register(
            4548, "energy from ac in 1 to battery", DataType.UINT32)
        energy_from_ac_in_2_to_ac_out = Register(
            4550, "energy from ac in 2 to ac out", DataType.UINT32)
        energy_from_ac_in_2_to_battery = Register(
            4552, "energy from ac in 2 to battery", DataType.UINT32)
        energy_from_ac_out_to_ac_in_1 = Register(
            4554, "energy from ac out to ac in 1", DataType.UINT32)
        energy_from_ac_out_to_ac_in_2 = Register(
            4556, "energy from ac out to ac in 2", DataType.UINT32)
        energy_from_battery_to_ac_in_1 = Register(
            4558, "energy from battery to ac in 1", DataType.UINT32)
        energy_from_battery_to_ac_in_2 = Register(
            4560, "energy from battery to ac in 2", DataType.UINT32)
        energy_from_battery_to_ac_out = Register(
            4562, "energy from battery to ac out", DataType.UINT32)
        energy_from_ac_out_to_battery = Register(
            4564, "energy from ac out to battery", DataType.UINT32)
        energy_from_solar_to_ac_in_1 = Register(
            4566, "energy from solar to ac in 1", DataType.UINT32)
        energy_from_solar_to_ac_in_2 = Register(
            4568, "energy from solar to ac in 2", DataType.UINT32)
        energy_from_solar_to_ac_out = Register(
            4570, "energy from solar to ac out", DataType.UINT32)
        energy_from_solar_to_battery = Register(
            4572, "energy from solar to battery", DataType.UINT32)
        yield_today = Register(
            4574, "yield today", DataType.UINT16)
        maximum_charge_power_today = Register(
            4575, "maximum charge power today", DataType.UINT16)
        yield_yesterday = Register(
            4576, "yield yesterday", DataType.UINT16)
        maximum_charge_power_yesterday = Register(
            4577, "maximum charge power yesterday", DataType.UINT16)
        yield_today_for_tracker_0 = Register(
            4578, "yield today for tracker 0", DataType.UINT16)
        yield_today_for_tracker_1 = Register(
            4579, "yield today for tracker 1", DataType.UINT16)
        yield_today_for_tracker_2 = Register(
            4580, "yield today for tracker 2", DataType.UINT16)
        yield_today_for_tracker_3 = Register(
            4581, "yield today for tracker 3", DataType.UINT16)
        yield_yesterday_for_tracker_0 = Register(
            4582, "yield yesterday for tracker 0", DataType.UINT16)
        yield_yesterday_for_tracker_1 = Register(
            4583, "yield yesterday for tracker 1", DataType.UINT16)
        yield_yesterday_for_tracker_2 = Register(
            4584, "yield yesterday for tracker 2", DataType.UINT16)
        yield_yesterday_for_tracker_3 = Register(
            4585, "yield yesterday for tracker 3", DataType.UINT16)
        maximum_charge_power_today_for_tracker_0 = Register(
            4586, "maximum charge power today for tracker 0", DataType.UINT16)
        maximum_charge_power_today_for_tracker_1 = Register(
            4587, "maximum charge power today for tracker 1", DataType.UINT16)
        maximum_charge_power_today_for_tracker_2 = Register(
            4588, "maximum charge power today for tracker 2", DataType.UINT16)
        maximum_charge_power_today_for_tracker_3 = Register(
            4589, "maximum charge power today for tracker 3", DataType.UINT16)
        maximum_charge_power_yesterday_tracker_0 = Register(
            4590, "maximum charge power yesterday tracker 0", DataType.UINT16)
        maximum_charge_power_yesterday_tracker_1 = Register(
            4591, "maximum charge power yesterday tracker 1", DataType.UINT16)
        maximum_charge_power_yesterday_tracker_2 = Register(
            4592, "maximum charge power yesterday tracker 2", DataType.UINT16)
        maximum_charge_power_yesterday_tracker_3 = Register(
            4593, "maximum charge power yesterday tracker 3", DataType.UINT16)
        pv_voltage_for_tracker_0 = Register(
            4594, "pv voltage for tracker 0", DataType.UINT16)
        pv_voltage_for_tracker_1 = Register(
            4595, "pv voltage for tracker 1", DataType.UINT16)
        pv_voltage_for_tracker_2 = Register(
            4596, "pv voltage for tracker 2", DataType.UINT16)
        pv_voltage_for_tracker_3 = Register(
            4597, "pv voltage for tracker 3", DataType.UINT16)
        pv_power_for_tracker_0 = Register(
            4598, "pv power for tracker 0", DataType.UINT16)
        pv_power_for_tracker_1 = Register(
            4599, "pv power for tracker 1", DataType.UINT16)
        pv_power_for_tracker_2 = Register(
            4600, "pv power for tracker 2", DataType.UINT16)
        pv_power_for_tracker_3 = Register(
            4601, "pv power for tracker 3", DataType.UINT16)

    class VEbusRegisters(Enum):
        slave_id = 227
        input_voltage_phase_1 = Register(
            3, "input voltage phase 1", DataType.UINT16, gain=10)
        input_voltage_phase_2 = Register(
            4, "input voltage phase 2", DataType.UINT16, gain=10)
        input_voltage_phase_3 = Register(
            5, "input voltage phase 3", DataType.UINT16, gain=10)
        input_current_phase_1 = Register(
            6, "input current phase 1", DataType.INT16, gain=10)
        input_current_phase_2 = Register(
            7, "input current phase 2", DataType.INT16, gain=10)
        input_current_phase_3 = Register(
            8, "input current phase 3", DataType.INT16, gain=10)
        input_frequency_1 = Register(
            9, "input frequency 1", DataType.INT16, gain=100)
        input_frequency_2 = Register(
            10, "input frequency 2", DataType.INT16, gain=100)
        input_frequency_3 = Register(
            11, "input frequency 3", DataType.INT16, gain=100)
        input_power_phase_1 = Register(
            12, "input power phase 1", DataType.INT16, gain=0.1)
        input_power_phase_2 = Register(
            13, "input power phase 2", DataType.INT16, gain=0.1)
        input_power_phase_3 = Register(
            14, "input power phase 3", DataType.INT16, gain=0.1)
        output_voltage_phase_1 = Register(
            15, "output voltage phase 1", DataType.UINT16)
        output_voltage_phase_2 = Register(
            16, "output voltage phase 2", DataType.UINT16)
        output_voltage_phase_3 = Register(
            17, "output voltage phase 3", DataType.UINT16)
        output_current_phase_1 = Register(
            18, "output current phase 1", DataType.INT16)
        output_current_phase_2 = Register(
            19, "output current phase 2", DataType.INT16)
        output_current_phase_3 = Register(
            20, "output current phase 3", DataType.INT16)
        output_frequency = Register(21, "output frequency", DataType.UINT16)
        active_input_current_limit = Register(
            22, "active input current limit", DataType.INT16)
        output_power_phase_1 = Register(
            23, "output power phase 1", DataType.INT16, gain=0.1)
        output_power_phase_2 = Register(
            24, "output power phase 2", DataType.INT16, gain=0.1)
        output_power_phase_3 = Register(
            25, "output power phase 3", DataType.INT16, gain=0.1)
        battery_voltage = Register(26, "battery voltage", DataType.UINT16)
        battery_current = Register(27, "battery current", DataType.INT16)
        phase_count = Register(28, "phase count", DataType.UINT16)
        active_input = Register(29, "active input", DataType.UINT16)
        vebus_state_of_charge = Register(
            30, "vebus state of charge", DataType.UINT16)
        vebus_state = Register(31, "vebus state", DataType.UINT16)
        vebus_error = Register(32, "vebus error", DataType.UINT16)
        switch_position = Register(33, "switch position", DataType.UINT16)
        temperature_alarm = Register(34, "temperature alarm", DataType.UINT16)
        low_battery_alarm = Register(35, "low battery alarm", DataType.UINT16)
        overload_alarm = Register(36, "overload alarm", DataType.UINT16)
        ess_power_setpoint_phase_1 = Register(
            37, "ess power setpoint phase 1", DataType.INT16,
            access_type=AccessType.READ_WRITE)
        ess_disable_charge_flag_phase = Register(
            38, "ess disable charge flag phase", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ess_disable_feedback_flag_phase = Register(
            39, "ess disable feedback flag phase", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ess_power_setpoint_phase_2 = Register(
            40, "ess power setpoint phase 2", DataType.INT16,
            access_type=AccessType.READ_WRITE)
        ess_power_setpoint_phase_3 = Register(
            41, "ess power setpoint phase 3", DataType.INT16,
            access_type=AccessType.READ_WRITE)
        temperature_sensor_alarm = Register(
            42, "temperature sensor alarm", DataType.UINT16)
        voltage_sensor_alarm = Register(
            43, "voltage sensor alarm", DataType.UINT16)
        temperature_alarm_l1 = Register(
            44, "temperature alarm l1", DataType.UINT16)
        low_battery_alarm_l1 = Register(
            45, "low battery alarm l1", DataType.UINT16)
        overload_alarm_l1 = Register(46, "overload alarm l1", DataType.UINT16)
        ripple_alarm_l1 = Register(47, "ripple alarm l1", DataType.UINT16)
        temperature_alarm_l2 = Register(
            48, "temperature alarm l2", DataType.UINT16)
        low_battery_alarm_l2 = Register(
            49, "low battery alarm l2", DataType.UINT16)
        overload_alarm_l2 = Register(50, "overload alarm l2", DataType.UINT16)
        ripple_alarm_l2 = Register(51, "ripple alarm l2", DataType.UINT16)
        temperature_alarm_l3 = Register(
            52, "temperature alarm l3", DataType.UINT16)
        low_battery_alarm_l3 = Register(
            53, "low battery alarm l3", DataType.UINT16)
        overload_alarm_l3 = Register(54, "overload alarm l3", DataType.UINT16)
        ripple_alarm_l3 = Register(55, "ripple alarm l3", DataType.UINT16)
        disable_pv_inverter = Register(
            56, "disable pv inverter", DataType.UINT16)
        vebus_bms_allows_battery_to_be_charged = Register(
            57, "vebus bms allows battery to be charged", DataType.UINT16)
        vebus_bms_allows_battery_to_be_discharged = Register(
            58, "vebus bms allows battery to be discharged", DataType.UINT16)
        vebus_bms_is_expected = Register(
            59, "vebus bms is expected", DataType.UINT16)
        vebus_bms_error = Register(60, "vebus bms error", DataType.UINT16)
        battery_temperature = Register(
            61, "battery temperature", DataType.INT16)
        vebus_reset = Register(62, "vebus reset", DataType.UINT16)
        phase_rotation_warning = Register(
            63, "phase rotation warning", DataType.UINT16)
        grid_lost_alarm = Register(64, "grid lost alarm", DataType.UINT16)
        feed_dc_overvoltage_into_grid = Register(
            65, "feed dc overvoltage into grid", DataType.UINT16)
        maximum_overvoltage_feed_in_power_l1 = Register(
            66, "maximum overvoltage feed in power l1", DataType.UINT16)
        maximum_overvoltage_feed_in_power_l2 = Register(
            67, "maximum overvoltage feed in power l2", DataType.UINT16)
        maximum_overvoltage_feed_in_power_l3 = Register(
            68, "maximum overvoltage feed in power l3", DataType.UINT16)

    class GridRegisters(Enum):
        grid_l1_power = Register(2600, "grid l1 power", DataType.INT16)
        grid_l2_power = Register(2601, "grid l2 power", DataType.INT16)
        grid_l3_power = Register(2602, "grid l3 power", DataType.INT16)
        grid_l1_energy_from_net = Register(
            2603, "grid l1 energy from net", DataType.UINT16, gain=100)
        grid_l2_energy_from_net = Register(
            2604, "grid l2 energy from net", DataType.UINT16, gain=100)
        grid_l3_energy_from_net = Register(
            2605, "grid l3 energy from net", DataType.UINT16, gain=100)
        grid_l1_energy_to_net = Register(
            2606, "grid l1 energy to net", DataType.UINT16, gain=100)
        grid_l2_energy_to_net = Register(
            2607, "grid l2 energy to net", DataType.UINT16, gain=100)
        grid_l3_energy_to_net = Register(
            2608, "grid l3 energy to net", DataType.UINT16, gain=100)
        serial = Register(2609, "serial", DataType.STRING, count=14)
        grid_l1_voltage = Register(
            2616, "grid l1 voltage", DataType.UINT16, gain=10)
        grid_l1_current = Register(
            2617, "grid l1 current", DataType.INT16, gain=10)
        grid_l2_voltage = Register(
            2618, "grid l2 voltage", DataType.UINT16, gain=10)
        grid_l2_current = Register(
            2619, "grid l2 current", DataType.INT16, gain=10)
        grid_l3_voltage = Register(
            2620, "grid l3 voltage", DataType.UINT16, gain=10)
        grid_l3_current = Register(
            2621, "grid l3 current", DataType.INT16, gain=10)
        grid_l1_energy_from_net_2 = Register(
            2622, "grid l1 energy from net", DataType.UINT32, gain=100)
        grid_l2_energy_from_net_2 = Register(
            2624, "grid l2 energy from net", DataType.UINT32, gain=100)
        grid_l3_energy_from_net_2 = Register(
            2626, "grid l3 energy from net", DataType.UINT32, gain=100)
        grid_l1_energy_to_net_2 = Register(
            2628, "grid l1 energy to net", DataType.UINT32, gain=100)
        grid_l2_energy_to_net_2 = Register(
            2630, "grid l2 energy to net", DataType.UINT32, gain=100)
        grid_l3_energy_to_net_2 = Register(
            2632, "grid l3 energy to net", DataType.UINT32, gain=100)
