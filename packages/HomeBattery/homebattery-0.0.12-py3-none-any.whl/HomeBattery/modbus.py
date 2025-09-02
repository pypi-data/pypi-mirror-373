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

This module provides a set of classes and functions to interact with Modbus
devices. It includes definitions for Modbus registers, data types, and access
types, as well as a ModbusDevice class that facilitates reading from and
writing to Modbus devices using the pymodbus library.

Classes:
    AccessType: Enum representing the access types of a Modbus register.
    DataType: Enum representing the data types of a Modbus register.
    Register: Dataclass representing a Modbus register.
    ModbusDevice: Class representing a Modbus device and providing methods to
                  interact with it.

Usage:
    Create an instance of the ModbusDevice class with the IP address and port
    of the Modbus device. Use the provided methods to read from and write to
    the Modbus device registers.
"""


from enum import Enum
from dataclasses import dataclass

from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian


class AccessType(Enum):
    READ = "r"
    WRITE = "w"
    READ_WRITE = "rw"


class DataType(Enum):
    INT16 = "int16"
    UINT16 = "uint16"
    INT32 = "int32"
    UINT32 = "uint32"
    INT64 = "int64"
    UINT64 = "uint64"
    STRING = "string"


@dataclass
class Register:
    '''Represents a modbus register

    Arguments:
        address (int): the address of the register
        name (str): the name of the register
        data_type (DataType): the data type of the register
        byte_order (Endian): the byte order of the register
        count (int): the number of registers
        gain (float): the gain of the register
        unit (str): the unit of the register
        access_type (AccessType): the access type of the register
        mapping (dict): the mapping of the register
    '''
    address: int
    name: str = None
    data_type: DataType = DataType.INT16
    byte_order: Endian = Endian.BIG
    count: int = 1
    gain: float = 1
    unit: str = None
    access_type: AccessType = AccessType.READ
    mapping: dict = None

    def __post_init__(self):
        if self.data_type in [DataType.INT32, DataType.UINT32]:
            self.count = 2
        elif self.data_type in [DataType.INT64, DataType.UINT64]:
            self.count = 4

    def __str__(self):
        return f"Register: {self.address}, {self.name}, {self.data_type}, \
                {self.byte_order}, {self.count}, {self.gain}, {self.unit}, \
                {self.access_type}, {self.mapping}"

    def decode(self, value: any):
        '''Decodes the value of the register

        Arguments:
            value: the value of the register

        Returns:
            the decoded value of the register
        '''
        if self.data_type is None:
            raise ValueError(f"Data type not set, please provide register \
                             with a data type! \n {self}")

        decoder = BinaryPayloadDecoder.fromRegisters(value, self.byte_order)
        if self.data_type == DataType.INT16:
            return decoder.decode_16bit_int() / self.gain
        elif self.data_type == DataType.UINT16:
            return decoder.decode_16bit_uint() / self.gain
        elif self.data_type == DataType.INT32:
            return decoder.decode_32bit_int() / self.gain
        elif self.data_type == DataType.UINT32:
            return decoder.decode_32bit_uint() / self.gain
        elif self.data_type == DataType.INT64:
            return decoder.decode_64bit_int() / self.gain
        elif self.data_type == DataType.UINT64:
            return decoder.decode_64bit_uint() / self.gain
        elif self.data_type == DataType.STRING:
            return decoder.decode_string(self.count * 2)

    def build_payload(self, value: any):
        '''Builds the payload of the register

        Arguments:
            value: the value of the register

        Returns:
            the payload of the register
        '''
        if self.data_type is None:
            raise ValueError(f"Data type not set, please provide register \
                             with a data type! \n {self}")

        builder = BinaryPayloadBuilder(byteorder=self.byte_order)
        if self.data_type == DataType.STRING:
            builder.add_string(value)
        else:
            value = int(value * self.gain)
            if self.data_type == DataType.INT16:
                builder.add_16bit_int(value)
            elif self.data_type == DataType.UINT16:
                builder.add_16bit_uint(value)
            elif self.data_type == DataType.INT32:
                builder.add_32bit_int(value)
            elif self.data_type == DataType.UINT32:
                builder.add_32bit_uint(value)
            elif self.data_type == DataType.INT64:
                builder.add_64bit_int(value)
            elif self.data_type == DataType.UINT64:
                builder.add_64bit_uint(value)
        return builder.to_registers()


class ModbusDevice:
    '''Represents a modbus device

    Arguments:
        modbus_ip (str): ip address of the modbus device
        modbus_port (int): port of the modbus device
        timeout (int): connection request timeout of the modbus device in
                       seconds
    '''

    def __init__(
            self,
            modbus_ip: str,
            modbus_port: int = 502,
            timeout: int = 3
    ):
        self._modbus_ip = modbus_ip
        self._modbus_port = modbus_port
        self._timeout = timeout
        self._client = ModbusTcpClient(
            self._modbus_ip,
            port=self._modbus_port,
            timeout=timeout
        )
        self.connect()

    def connect(self):
        '''Connects to the modbus device'''
        if not self._client.connected:
            self._client.connect()
            assert self._client.connected

    def disconnect(self):
        '''Disconnects from the modbus device'''
        self._client.close()

    def read_coils(self, address: int, count: int = 1, slave_id: int = 1):
        '''Reads coils (code 0x01) from the modbus battery

        Arguments:
            address (int): the address of the coils
            count (int): the number of coils to read
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        response = self._client.read_coils(address, count, slave_id)
        return response.bits

    def read_discrete_inputs(self, address: int, count: int = 1,
                             slave_id: int = 1):
        '''Reads discrete inputs (code 0x02) from the modbus battery

        Arguments:
            address (int): the address of the discrete inputs
            count (int): the number of discrete inputs to read
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        response = self._client.read_discrete_inputs(
            address, count, slave_id)
        return response.bits

    def read_holding_register(self, register: Register, slave_id: int = 1):
        '''Reads holding registers (code 0x03) from the modbus battery

        Arguments:
            register (Register): the register to read
            slave_id (int): the id of the slave

        Returns:
            the decoded value of the register
        '''
        if not self._client.connected:
            raise Exception("Client not connected")
        if (register.access_type != AccessType.READ and
                register.access_type != AccessType.READ_WRITE):
            raise Exception(f"Register {register.name} does not have read \
                            access")

        response = self._client.read_holding_registers(
            register.address, register.count, slave_id)
        if response.isError():
            print("Error reading holding register")
            print(response)
            return None
        return register.decode(response.registers)

    def read_holding_register_raw(self, address: int, count: int = 1,
                                  slave_id: int = 1):
        '''Reads holding registers (code 0x03) from the modbus battery

        Arguments:
            address (int): the address of the holding registers
            count (int): the number of holding registers to read
            slave_id (int): the id of the slave

        Returns:
            the raw modbus response
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        response = self._client.read_holding_registers(
            address, count, slave_id)
        if response.isError():
            print("Error reading holding register")
            print(response)
            return None
        return response.registers

    def read_input_register(self, register: Register, slave_id: int = 1):
        '''Reads input registers (code 0x04) from the modbus battery

        Arguments:
            register (Register): the register to read
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")
        if (register.access_type != AccessType.READ and
                register.access_type != AccessType.READ_WRITE):
            raise Exception(f"Register {register.name} does not have read \
                            access")

        response = self._client.read_holding_registers(
            register.address, register.count, slave_id)
        if response.isError():
            print("Error reading holding register")
            print(response)
            return None
        return register.decode(response.registers)

    def read_input_register_raw(self, address: int, count: int = 1,
                                slave_id: int = 1):
        '''Reads input registers (code 0x04) from the modbus battery

        Arguments:
            address (int): the address of the input registers
            count (int): the number of input registers to read
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        response = self._client.read_input_registers(
            address, count, slave_id)
        if response.isError():
            print("Error reading holding register")
            print(response)
            return None
        return response.registers

    def write_coil(self, address: int, value: bool, slave_id: int = 1):
        '''Writes a single coil (code 0x05) to the modbus battery

        Arguments:
            address (int): the address of the coil
            value (bool): the value of the coil
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        self._client.write_coil(address, value, slave_id)

    def write_register(self, register: Register, value: any,
                       slave_id: int = 1, force_0x10: bool = False):
        '''Writes a register (code 0x06 / 0x10) to the modbus battery using
        BinaryPayloadBuilder to build the payload

        Arguments:
            register (Register): the register to write
            value (int): the value of the register
            slave_id (int): the id of the slave
            force_0x10 (bool): force the use of function code 0x10
        '''
        if not self._client.connected:
            raise Exception("Client not connected")
        if (register.access_type != AccessType.WRITE and
                register.access_type != AccessType.READ_WRITE):
            raise Exception(f"Register {register.name} does not have write \
                            access")

        if register.count > 1:
            payload = register.build_payload(value)
            self._client.write_registers(
                register.address, payload, slave_id)
        else:
            payload = register.build_payload(value)
            if force_0x10:
                self._client.write_registers(
                    register.address, payload[0], slave_id)
            else:
                self._client.write_register(
                    register.address, payload[0], slave_id)

    def write_register_raw(self, address: int, value: int, slave_id: int = 1):
        '''Writes a single register (code 0x06) to the modbus battery

        Arguments:
            address (int): the address of the register
            value (int): the value of the register
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        self._client.write_register(address, value, slave_id)

    def write_coils(self, address: int, values: list[bool], slave_id: int = 1):
        '''Writes multiple coils (code 0x0F) to the modbus battery

        Arguments:
            address (int): the address of the coils
            values (list): the values of the coils
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        self._client.write_coils(address, values, slave_id)

    def write_registers(self, registers: list[Register], values: list[any],
                        slave_id: int = 1, force_0x10: bool = False):
        '''Writes multiple registers (code 0x10) to the modbus battery using
        BinaryPayloadBuilder to build the payload

        Arguments:
            registers (list): the registers to write
            values (list): the values of the registers
            slave_id (int): the id of the slave
            force_0x10 (bool): force the use of function code 0x10
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        for register, value in zip(registers, values):
            if (register.access_type != AccessType.WRITE and
                    register.access_type != AccessType.READ_WRITE):
                raise Exception(f"Register {register.name} does not have \
                                write access")

            if register.count > 1:
                payload = register.build_payload(value)
                self._client.write_registers(
                    register.address, payload, slave_id)
            else:
                payload = register.build_payload(value)
                if force_0x10:
                    self._client.write_registers(
                        register.address, payload[0], slave_id)
                else:
                    self._client.write_register(
                        register.address, payload[0], slave_id)

    def write_registers_raw(self, address: int, values: list[int],
                            slave_id: int = 1):
        '''Writes multiple registers (code 0x10) to the modbus battery

        Arguments:
            address (int): start address of the registers
            values (list): the values of the registers
            slave_id (int): the id of the slave
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        self._client.write_registers(address, values, slave_id)

    def read_all_registers(self, registers: list[Register], slave_id: int = 1):
        '''Reads all registers and returns a dict of all register names and
        values

        Arguments:
            registers (list): the registers to read
            slave_id (int): the id of the slave

        Returns:
            dict of all register names and values
        '''
        if not self._client.connected:
            raise Exception("Client not connected")

        values = {}

        for register in registers:
            if isinstance(register, Register):
                if (register.access_type == AccessType.READ or
                        register.access_type == AccessType.READ_WRITE):
                    values[register.name] = self.read_holding_register(
                        register, slave_id)
                else:
                    values[register.name] = "No read access"

        return values
