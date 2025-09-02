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

This module provides a class to interact with the Sun2000 inverter using Modbus
protocol. The Sun2000Inverter class allows for reading and writing various
parameters and settings of the inverter, such as power setpoints, battery state
of charge, and phase voltages.

The class inherits from ModbusBattery and utilizes the Register, AccessType,
and DataType classes from the modbus module to define and access the Modbus
registers of the inverter.
"""

import time
import warnings
from ..battery import ModbusBattery
from ..modbus import Register, AccessType, DataType
from enum import Enum


class Sun2000Inverter(ModbusBattery):
    '''Sun2000 inverter class

    Arguments:
        modbus_ip (str): the ip address of the modbus inverter
        modbus_port (int): the port of the modbus inverter
        timeout (int): the timeout of the modbus client in seconds
        capacity (int): the capacity of the inverter
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
        super().__init__(
            modbus_ip, modbus_port, timeout, capacity, max_charge_power,
            max_discharge_power, soc)

        time.sleep(1)

        self.init_power_setpoint_registers()

    def init_power_setpoint_registers(self):
        '''Prepare the inverter to accept power setpoints'''
        self.write_register(
            self.Sun2000Registers.ChargeFromGridFunction.value, 1)
        self.write_register(
            self.Sun2000Registers.ForcibleChargeDischargeSettingMode.value, 1)

    def _set_charge_setpoint(self, setpoint: int):
        '''Set the charge setpoint of the inverter

        Arguments:
            setpoint (int): the charge setpoint to set
        '''
        self.write_register(
            self.Sun2000Registers.TargetSOC.value, 1000)
        self.write_register(
            self.Sun2000Registers.ForcibleChargePower.value, setpoint)
        self.write_register(
            self.Sun2000Registers.ForcibleChargeDischarge.value, 1)

    def _set_discharge_setpoint(self, setpoint: int):
        '''Set the discharge setpoint of the inverter

        Arguments:
            setpoint (int): the discharge setpoint to set
        '''
        self.write_register(
            self.Sun2000Registers.TargetSOC.value, 50)
        self.write_register(
            self.Sun2000Registers.ForcibleDischargePower.value, setpoint)
        self.write_register(
            self.Sun2000Registers.ForcibleChargeDischarge.value, 2)

    def set_power_setpoint(self, setpoint: int):
        '''Set the power setpoint of the inverter

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
        elif setpoint < 0:
            self._set_discharge_setpoint(abs(setpoint))
        else:
            self.write_register(
                self.Sun2000Registers.ForcibleChargeDischarge.value, 0)

    def set_current_setpoint(self, setpoint: int):
        '''Set the current setpoint of the inverter

        Arguments:
            setpoint (int): the current setpoint to set in A
        '''
        phase_voltage = self.get_phase_voltage(1)
        power_setpoint = setpoint * phase_voltage
        self.set_power_setpoint(power_setpoint)

    def get_active_power_total(self):
        '''Get the total active power of the inverter

        Returns:
            float: the active power of the inverter in W
        '''
        return self.read_holding_register(
            self.Sun2000Registers.BatteryActivePower.value) * 1000

    def get_active_current_total(self):
        '''Get the total active current of the inverter

        Returns:
            float: the active current of the inverter in A
        '''
        return self.get_active_power_total() / self.get_phase_voltage(1)

    def get_battery_soc(self):
        '''Get the battery state of charge

        Returns:
            int: the battery state of charge
        '''
        return self.read_holding_register(
            self.Sun2000Registers.BatterySOC.value)

    def get_phase_voltage(self, phase: int):
        '''Get the phase voltage

        Arguments:
            phase (int): the phase to get the voltage from

        Returns:
            float: the phase voltage in V
        '''
        register = None
        if phase == 1:
            register = self.Sun2000Registers.PowerGridPhaseAVoltage.value
        elif phase == 2:
            register = self.Sun2000Registers.PowerGridPhaseBVoltage.value
        elif phase == 3:
            register = self.Sun2000Registers.PowerGridPhaseCVoltage.value
        if register:
            return self.read_holding_register(register)
        else:
            raise ValueError("Invalid phase")

    def get_phase_current(self, phase: int):
        '''Get the phase current

        Arguments:
            phase (int): the phase to get the current from

        Returns:
            float: the phase current in A
        '''
        register = None
        if phase == 1:
            register = self.Sun2000Registers.PowerGridPhaseACurrent.value
        elif phase == 2:
            register = self.Sun2000Registers.PowerGridPhaseBCurrent.value
        elif phase == 3:
            register = self.Sun2000Registers.PowerGridPhaseCCurrent.value
        if register:
            return self.read_holding_register(register)
        else:
            raise ValueError("Invalid phase")

    class Sun2000Registers(Enum):
        Model = Register(
            30000, "model", DataType.STRING, count=15,
            access_type=AccessType.READ)
        SerialNumber = Register(
            30015, "serial_number", DataType.STRING, count=10,
            access_type=AccessType.READ)
        ProductCode = Register(
            30025, "product_code", DataType.STRING, count=10,
            access_type=AccessType.READ)
        FirmwareVersion = Register(
            30035, "firmware_version", DataType.STRING, count=15,
            access_type=AccessType.READ)
        SoftwareVersion = Register(
            30050, "software_version", DataType.STRING, count=15,
            access_type=AccessType.READ)
        ProtocolVersion = Register(
            30068, "protocol_version", DataType.UINT32,
            access_type=AccessType.READ)
        ModelID = Register(
            30070, "model_id", DataType.UINT16, access_type=AccessType.READ)
        NumberOfStrings = Register(
            30071, "number_of_strings", DataType.UINT16,
            access_type=AccessType.READ)
        NumberOfMPPTs = Register(
            30072, "number_of_mppts", DataType.UINT16,
            access_type=AccessType.READ)
        RatedPower = Register(
            30073, "rated_power", DataType.UINT32, gain=1000,
            access_type=AccessType.READ)
        MaximumActivePowerR = Register(
            30075, "maximum_active_power", DataType.UINT32, gain=1000,
            access_type=AccessType.READ)
        MaximumApparantPower = Register(
            30077, "maximum_aparrant_power", DataType.UINT32, gain=1000,
            access_type=AccessType.READ)
        RealTimeMaximumReactivePowerFeedToGrid = Register(
            30079, "real_time_maximum_reactive_power_feed_to_grid",
            DataType.INT32, gain=1000, access_type=AccessType.READ)
        RealTimeMaximumReactivePowerAbsorbedFromGrid = Register(
            30081, "real_time_maximum_reactive_power_absorbed_from_grid",
            DataType.INT32, gain=1000, access_type=AccessType.READ)
        MaximumActiveCapability = Register(
            30083, "maximum_active_capability", DataType.UINT32, gain=1000,
            access_type=AccessType.READ)
        MaximumApparentCapability = Register(
            30085, "maximum_apparent_capability", DataType.UINT32, gain=1000,
            access_type=AccessType.READ)
        PowerGridPhaseAVoltage = Register(
            32069, "power_grid_phase_a_voltage", DataType.UINT16, gain=10,
            access_type=AccessType.READ)
        PowerGridPhaseBVoltage = Register(
            32070, "power_grid_phase_b_voltage", DataType.UINT16, gain=10,
            access_type=AccessType.READ)
        PowerGridPhaseCVoltage = Register(
            32071, "power_grid_phase_c_voltage", DataType.UINT16, gain=10,
            access_type=AccessType.READ)
        PowerGridPhaseACurrent = Register(
            32072, "power_grid_phase_a_current", DataType.INT32, gain=1000,
            count=2, access_type=AccessType.READ)
        PowerGridPhaseBCurrent = Register(
            32074, "power_grid_phase_b_current", DataType.INT32, gain=1000,
            count=2, access_type=AccessType.READ)
        PowerGridPhaseCCurrent = Register(
            32076, "power_grid_phase_c_current", DataType.INT32, gain=1000,
            count=2, access_type=AccessType.READ)
        ActivePower = Register(
            32080, "active_power", DataType.INT32, gain=1000,
            access_type=AccessType.READ)
        ReactivePower = Register(
            32082, "reactive_power", DataType.INT32, gain=1000,
            access_type=AccessType.READ)
        PowerFactorR = Register(
            32084, "power_factor", DataType.INT16, gain=1000,
            access_type=AccessType.READ)
        GridFrequency = Register(
            32085, "grid_frequency", DataType.UINT16, gain=100,
            access_type=AccessType.READ)
        InverterEfficiency = Register(
            32086, "inverter_efficiency", DataType.UINT16, gain=100,
            access_type=AccessType.READ)
        InternalTemperature = Register(
            32087, "internal_temperature", DataType.INT16, gain=10,
            access_type=AccessType.READ)
        InsulationImpedanceValue = Register(
            32088, "insulation_impedance_value", DataType.UINT16, gain=1000,
            access_type=AccessType.READ)
        DeviceStatus = Register(
            32089, "device_status", DataType.UINT16,
            access_type=AccessType.READ)
        FaultCode = Register(
            32090, "fault_code", DataType.UINT16, access_type=AccessType.READ)
        StartupTime = Register(
            32091, "startup_time", DataType.UINT32,
            access_type=AccessType.READ)
        ShutdownTime = Register(
            32093, "shutdown_time", DataType.UINT32,
            access_type=AccessType.READ)
        ActivePowerFast = Register(
            32095, "active_power_fast", DataType.INT32, gain=1000,
            access_type=AccessType.READ)
        SystemTime = Register(
            40000, "system_time", DataType.UINT32, count=2,
            access_type=AccessType.READ_WRITE)
        Q_UCharacteristicCurveModel = Register(
            40037, "q_u_characteristic_curve_model", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        Q_USchedulingTriggerPowerPercentage = Register(
            40038, "q_u_scheduling_trigger_power_percentage", DataType.INT16,
            access_type=AccessType.READ_WRITE)
        ActivePowerFixedValueDerating = Register(
            40120, "active_power_fixed_value_derating", DataType.UINT16,
            gain=10, access_type=AccessType.READ_WRITE)
        PowerFactorW = Register(
            40122, "power_factor", DataType.INT16, gain=1000,
            access_type=AccessType.READ_WRITE)
        ReactivePowerCompensation = Register(
            40123, "reactive_power_compensation", DataType.INT16, gain=1000,
            access_type=AccessType.READ_WRITE)
        ReactivePowerAdjustmentTime = Register(
            40124, "reactive_power_adjustment_time", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ActivePowerPercentageDerating = Register(
            40125, "active_power_percentage_derating", DataType.INT16,
            gain=10, access_type=AccessType.READ_WRITE)
        ActivePowerFixedValueDerating2 = Register(
            40126, "active_power_fixed_value_derating", DataType.UINT32,
            count=2, access_type=AccessType.READ_WRITE)
        ReactivePowerCompensationAtNight = Register(
            40128, "reactive_power_compensation_at_night", DataType.INT16,
            gain=1000, access_type=AccessType.READ_WRITE)
        FixedReactivePowerAtNight = Register(
            40129, "fixed_reactive_power_at_night", DataType.INT32, gain=1000,
            count=2, access_type=AccessType.READ_WRITE)
        CharacteristiccurveReactivepoweradjustmentTime = Register(
            40196, "characteristiccurve_reactivepoweradjustment_time",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        PercentApparentPower = Register(
            40197, "percent_apparent_power", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        Q_USchedulingExitPowerPercentage = Register(
            40198, "q_u_scheduling_exit_power_percentage", DataType.INT16,
            access_type=AccessType.READ_WRITE)
        ActivePowerPercentageControl = Register(
            40199, "active_power_percentage_control", DataType.INT16, gain=10,
            access_type=AccessType.READ_WRITE)
        PowerOn = Register(
            40200, "power_on", DataType.UINT16, access_type=AccessType.WRITE)
        Shutdown = Register(
            40201, "shutdown", DataType.UINT16, access_type=AccessType.WRITE)
        Reset = Register(
            40205, "reset", DataType.UINT16, access_type=AccessType.WRITE)
        GridStandardCode = Register(
            42000, "grid_standard_code", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        OutputMode = Register(
            42001, "output_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        VoltageLevel = Register(
            42002, "voltage_level", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        FrequencyLevel = Register(
            42003, "frequency_level", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        RemotePowerScheduling = Register(
            42014, "remote_power_scheduling", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ReactivePowerVariationGradient = Register(
            42015, "reactive_power_variation_gradient", DataType.UINT32,
            gain=1000, count=2, access_type=AccessType.READ_WRITE)
        ActivePowerGradient = Register(
            42017, "active_power_gradient", DataType.UINT32, gain=1000,
            count=2, access_type=AccessType.READ_WRITE)
        SchedulingInstructionMaintenanceTime = Register(
            42019, "scheduling_instruction_maintenance_time", DataType.UINT32,
            count=2, access_type=AccessType.READ_WRITE)
        MaximumApparentPower = Register(
            42021, "maximum_apparent_power", DataType.UINT32, gain=1000,
            count=2, access_type=AccessType.READ_WRITE)
        MaximumActivePowerW = Register(
            42023, "maximum_active_power", DataType.UINT32, gain=1000, count=2,
            access_type=AccessType.READ_WRITE)
        ApparentPowerReference = Register(
            42025, "apparent_power_reference", DataType.UINT32, gain=1000,
            count=2, access_type=AccessType.READ_WRITE)
        ActivePowerReference = Register(
            42027, "active_power_reference", DataType.UINT32, gain=1000,
            count=2, access_type=AccessType.READ_WRITE)
        ActivePowerGradientOfPowerStation = Register(
            42029, "active_power_gradient_of_power_station", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        FilteringTimeOfTheAverageActivePowerOfThePowerStation = Register(
            42030,
            "filtering_time_of_the_average_active_power_of_the_power_station",
            DataType.UINT32, count=2, access_type=AccessType.READ_WRITE)
        PF_UVoltageDetectionFilterTime = Register(
            42032, "pf_u_voltage_detection_filter_time", DataType.UINT16,
            gain=10, access_type=AccessType.READ_WRITE)
        FrequencyDetectionFilterTime = Register(
            42037, "frequency_detection_filter_time", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        FrequencyActiveDeratingRecoveryDelayTime = Register(
            42040, "frequency_active_derating_recovery_delay_time",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        EffectiveDelayTimeOfActiveFrequencyDerating = Register(
            42041, "effective_delay_time_of_active_frequency_derating",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        FrequencyActiveDeratingHysteresisLoop = Register(
            42042, "frequency_active_derating_hysteresis_loop",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        FMControlResponseDeadZone = Register(
            42043, "fm_control_response_dead_zone", DataType.UINT16, gain=1000,
            access_type=AccessType.READ_WRITE)
        PQMode = Register(
            42046, "pq_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        PanelType = Register(
            42047, "panel_type", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        PIDCompensationDirection = Register(
            42048, "pid_compensation_direction", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        StringConnectionMode = Register(
            42049, "string_connection_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        IsolationSettings = Register(
            42050, "isolation_settings", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        FrequencyModulationControlPowerVariationGradient = Register(
            42051, "frequency_modulation_control_power_variation_gradient",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        FMControlPowerVariationLimit = Register(
            42052, "fm_control_power_variation_limit", DataType.UINT16,
            gain=10, access_type=AccessType.READ_WRITE)
        FMControlDelayResponseTime = Register(
            42053, "fm_control_delay_response_time", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        MPPTMultimodalScanning = Register(
            42054, "mppt_multimodal_scanning", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        MPPTScanningInterval = Register(
            42055, "mppt_scanning_interval", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        MPPTPredictedPower = Register(
            42056, "mppt_predicted_power", DataType.UINT32, gain=1000, count=2,
            access_type=AccessType.READ)
        AutomaticPowerGridFaultRecovery = Register(
            42061, "automatic_power_grid_fault_recovery", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        PowerLimit0Shutdown = Register(
            42062, "power_limit_0_shutdown", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        AutomaticShutoffOfCommunicationLinkDisconnection = Register(
            42063, "automatic_shutoff_of_communication_link_disconnection",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        CommunicationResumesAutomaticPowerOn = Register(
            42064, "communication_resumes_automatic_power_on", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        PowerQualityOptimizationMode = Register(
            42065, "power_quality_optimization_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        RCDEnhancement = Register(
            42066, "rcd_enhancement", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        NoTimeWork = Register(
            42067, "no_time_work", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        NightPIDProtection = Register(
            42069, "night_pid_protection", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ReactivePowerParameterTakesEffectAtNight = Register(
            42070, "reactive_power_parameter_takes_effect_at_night",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        CommunicationDisconnectionDetectionTime = Register(
            42072, "communication_disconnection_detection_time",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        AFCI = Register(
            42073, "afci", DataType.UINT16, access_type=AccessType.READ_WRITE)
        AFCIDetectionAdaptationMode = Register(
            42074, "afci_detection_adaptation_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        CommunicationLinkDisconnectionFailureProtection = Register(
            42075, "communication_link_disconnection_failure_protection",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        FailSafeActivePowerMode = Register(
            42076, "fail_safe_active_power_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ActivePowerLimitForFailProtection = Register(
            42077, "active_power_limit_for_fail_protection", DataType.UINT32,
            gain=10, count=2, access_type=AccessType.READ_WRITE)
        FailSafeReactivePowerMode = Register(
            42079, "fail_safe_reactive_power_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        FrequencyChangeRateProtection = Register(
            42080, "frequency_change_rate_protection", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        FrequencyChangeRateProtectionPoint = Register(
            42081, "frequency_change_rate_protection_point", DataType.UINT16,
            gain=10, access_type=AccessType.READ_WRITE)
        FrequencyChangeRateProtectionTime = Register(
            42082, "frequency_change_rate_protection_time", DataType.UINT16,
            gain=10, access_type=AccessType.READ_WRITE)
        FailProtectionReactivePowerLimit = Register(
            42083, "fail_protection_reactive_power_limit", DataType.INT16,
            gain=1000, access_type=AccessType.READ_WRITE)
        PowerOnVoltageUpperLimit = Register(
            42084, "power_on_voltage_upper_limit", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        LowerLimitOfGridConnectedPowerOnVoltage = Register(
            42085, "lower_limit_of_grid_connected_power_on_voltage",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        UpperLimitOfGridComingStartupFrequency = Register(
            42086, "upper_limit_of_grid_coming_startup_frequency",
            DataType.UINT16, gain=100, access_type=AccessType.READ_WRITE)
        LowerLimitOfPowerOnFrequency = Register(
            42087, "lower_limit_of_power_on_frequency", DataType.UINT16,
            gain=100, access_type=AccessType.READ_WRITE)
        UpperLimitOfPowerGridReconnectionVoltage = Register(
            42088, "upper_limit_of_power_grid_reconnection_voltage",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        LowerLimitOfPowerGridReconnectionVoltage = Register(
            42089, "lower_limit_of_power_grid_reconnection_voltage",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        UpperLimitOfPowerGridReconnectionFrequency = Register(
            42090, "upper_limit_of_power_grid_reconnection_frequency",
            DataType.UINT16, gain=100, access_type=AccessType.READ_WRITE)
        LowerLimitOfPowerGridReconnectionFrequency = Register(
            42091, "lower_limit_of_power_grid_reconnection_frequency",
            DataType.UINT16, gain=100, access_type=AccessType.READ_WRITE)
        AutomaticPowerGridReconnectionTime = Register(
            42092, "automatic_power_grid_reconnection_time", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ComponentNameplateShortCircuitCurrent = Register(
            42093, "component_nameplate_short_circuit_current",
            DataType.UINT16, gain=100, access_type=AccessType.READ_WRITE)
        InsulationImpedanceProtectionPoint = Register(
            42097, "insulation_impedance_protection_point", DataType.UINT16,
            gain=1000, access_type=AccessType.READ_WRITE)
        VoltageUnbalanceProtectionPoint = Register(
            42098, "voltage_unbalance_protection_point", DataType.UINT16,
            gain=10, access_type=AccessType.READ_WRITE)
        PhaseProtectionPoint = Register(
            42099, "phase_protection_point", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        PowerGridFaultStartupSoftStartTime = Register(
            42100, "power_grid_fault_startup_soft_start_time", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        CosphiPPnTriggerVoltage = Register(
            42101, "cosphi_ppn_trigger_voltage", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        CosphiPPnExitVoltage = Register(
            42102, "cosphi_ppn_exit_voltage", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        SoftStartTime = Register(
            42103, "soft_start_time", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        PowerGridFaultRecoveryAndGridConnectedTime = Register(
            42104, "power_grid_fault_recovery_and_grid_connected_time",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        ShortTimePowerGridInterruptionJudgmentTime = Register(
            42105, "short_time_power_grid_interruption_judgment_time",
            DataType.UINT32, gain=1000, count=2,
            access_type=AccessType.READ_WRITE)
        ShutdownGradient = Register(
            42107, "shutdown_gradient", DataType.UINT32, gain=1000, count=2,
            access_type=AccessType.READ_WRITE)
        LineLossCompensation = Register(
            42109, "line_loss_compensation", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        GridFaultZeroCurrentMode = Register(
            42110, "grid_fault_zero_current_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        PowerGridVoltageJumpTriggerThreshold = Register(
            42111, "power_grid_voltage_jump_trigger_threshold",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        HVRT = Register(
            42112, "hvrt", DataType.UINT16, access_type=AccessType.READ_WRITE)
        HVRTTriggerThreshold = Register(
            42113, "hvrt_trigger_threshold", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        HVRTPositiveReactiveCompensationFactor = Register(
            42114, "hvrt_positive_reactive_compensation_factor",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        ShortTimePowerGridInterruptionAndQuickStartup = Register(
            42116, "short_time_power_grid_interruption_and_quick_startup",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        LVRTActiveCurrentMaintenanceCoefficient = Register(
            42118, "lvrt_active_current_maintenance_coefficient",
            DataType.UINT16, gain=100, access_type=AccessType.READ_WRITE)
        LVRT = Register(
            42119, "lvrt", DataType.UINT16, access_type=AccessType.READ_WRITE)
        LVRTTriggerThreshold = Register(
            42120, "lvrt_trigger_threshold", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        PowerGridVoltageProtectionShieldingDuringVRT = Register(
            42121, "power_grid_voltage_protection_shielding_during_vrt",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        LVRTPositiveSequenceReactiveCompensationFactor = Register(
            42122, "lvrt_positive_sequence_reactive_compensation_factor",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        VRTExitHysteresisThreshold = Register(
            42123, "vrt_exit_hysteresis_threshold", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        VRTActiveCurrentLimitPercentage = Register(
            42124, "vrt_active_current_limit_percentage", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        VRTActivePowerRecoveryGradient = Register(
            42125, "vrt_active_power_recovery_gradient", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        HVRTNegativeSequenceReactivePowerCompensationFactor = Register(
            42126, "hvrt_negative_sequence_reactive_power_compensation_factor",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        LVRTNegativeSequenceReactivePowerCompensationFactor = Register(
            42127, "lvrt_negative_sequence_reactive_power_compensation_factor",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        PhaseAngleOffsetProtection = Register(
            42128, "phase_angle_offset_protection", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ActiveIslandProtection = Register(
            42129, "active_island_protection", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        PassiveIslandProtection = Register(
            42130, "passive_island_protection", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        OVGRAssociatedShutdown = Register(
            42131, "ovgr_associated_shutdown", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        DryContactFunction = Register(
            42132, "dry_contact_function", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        LVRTReactiveCurrentLimitPercentage = Register(
            42133, "lvrt_reactive_current_limit_percentage", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        LVRTZeroCurrentModeThreshold = Register(
            42134, "lvrt_zero_current_mode_threshold", DataType.UINT16,
            gain=10, access_type=AccessType.READ_WRITE)
        LVRTMode = Register(
            42135, "lvrt_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        VoltageRiseSuppression = Register(
            42138, "voltage_rise_suppression", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        VoltageRiseSuppressionReactivePowerAdjustmentPoint = Register(
            42139, "voltage_rise_suppression_reactive_power_adjustment_point",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        VoltageRiseSuppressionActiveDeratingPoint = Register(
            42140, "voltage_rise_suppression_active_derating_point",
            DataType.UINT16, gain=10, access_type=AccessType.READ_WRITE)
        FMControl = Register(
            42141, "fm_control", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        FrequencyModulationControlDifferentialRate = Register(
            42142, "frequency_modulation_control_differential_rate",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        OverfrequencyDerating = Register(
            42143, "overfrequency_derating", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        OverfrequencyDeratingCutoffFrequency = Register(
            42144, "overfrequency_derating_cutoff_frequency", DataType.UINT16,
            gain=100, access_type=AccessType.READ_WRITE)
        OverfrequencyDeratingCutoffPower = Register(
            42145, "overfrequency_derating_cutoff_power", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        OverfrequencyDeratingTriggerFrequency = Register(
            42146, "overfrequency_derating_trigger_frequency",
            DataType.UINT16, gain=100, access_type=AccessType.READ_WRITE)
        OverfrequencyDeratingExitFrequency = Register(
            42147, "overfrequency_derating_exit_frequency", DataType.UINT16,
            gain=100, access_type=AccessType.READ_WRITE)
        OverfrequencyDeratingPowerRecoveryGradient = Register(
            42148, "overfrequency_derating_power_recovery_gradient",
            DataType.UINT16, access_type=AccessType.READ_WRITE)
        UnderfrequencyPowerIncrease = Register(
            42151, "underfrequency_power_increase", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        UnderfrequencyPowerRecoveryGradient = Register(
            42152, "underfrequency_power_recovery_gradient", DataType.UINT16,
            access_type=AccessType.READ_WRITE)

        # battery registers
        BatterySOC = Register(
            37760, "battery_soc", DataType.UINT16, gain=10,
            access_type=AccessType.READ)
        BatteryVoltage = Register(
            37763, "battery_voltage", DataType.UINT16, gain=10,
            access_type=AccessType.READ)
        BatteryActivePower = Register(
            37765, "battery_active_power", DataType.INT32, gain=1000, count=2,
            access_type=AccessType.READ)
        ForcedChargingAndDischargingPeriod = Register(
            47083, "forced_charging_and_discharging_period", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ChargeFromGridFunction = Register(
            47087, "charge_from_grid_function", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ForcibleChargeDischarge = Register(
            47100, "forcible_charge_discharge", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        TargetSOC = Register(
            47101, "target_soc", DataType.UINT16, gain=10,
            access_type=AccessType.READ_WRITE)
        ForcibleChargeDischargeSettingMode = Register(
            47246, "forcible_charge_discharge_setting_mode", DataType.UINT16,
            access_type=AccessType.READ_WRITE)
        ForcibleChargePower = Register(
            47247, "forcible_charge_power", DataType.UINT32, gain=1000,
            count=2, access_type=AccessType.READ_WRITE)
        ForcibleDischargePower = Register(
            47249, "forcible_discharge_power", DataType.UINT32, gain=1000,
            count=2, access_type=AccessType.READ_WRITE)
