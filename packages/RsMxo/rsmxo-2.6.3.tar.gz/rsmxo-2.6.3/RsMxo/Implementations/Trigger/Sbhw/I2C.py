from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class I2CCls:
	"""I2C commands group definition. 12 total commands, 0 Subgroups, 12 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("i2C", core, parent)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.SbusI2cTriggerType:
		"""TRIGger:SBHW:I2C:TYPE \n
		Snippet: value: enums.SbusI2cTriggerType = driver.trigger.sbhw.i2C.get_type_py() \n
		Selects the trigger type for I²C analysis. \n
			:return: type_py:
				- STARt: Start condition
				- REPStart: Repeated start - the start condition occurs without previous stop condition.
				- STOP: Stop condition, end of frame
				- NACK: Missing acknowledge bit. To localize specific missing acknowledge bits, use:TRIGger:SBHW:I2C:ADNackTRIGger:SBHW:I2C:DWNackTRIGger:SBHW:I2C:DRNack
				- ADDRess: Triggers on one specific address
				- DATA: Triggers on a specific data
				- ADAT: Triggers on a combination of address and data condition."""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusI2cTriggerType)

	def set_type_py(self, type_py: enums.SbusI2cTriggerType) -> None:
		"""TRIGger:SBHW:I2C:TYPE \n
		Snippet: driver.trigger.sbhw.i2C.set_type_py(type_py = enums.SbusI2cTriggerType.ADAT) \n
		Selects the trigger type for I²C analysis. \n
			:param type_py:
				- STARt: Start condition
				- REPStart: Repeated start - the start condition occurs without previous stop condition.
				- STOP: Stop condition, end of frame
				- NACK: Missing acknowledge bit. To localize specific missing acknowledge bits, use:TRIGger:SBHW:I2C:ADNackTRIGger:SBHW:I2C:DWNackTRIGger:SBHW:I2C:DRNack
				- ADDRess: Triggers on one specific address
				- DATA: Triggers on a specific data
				- ADAT: Triggers on a combination of address and data condition."""
		param = Conversions.enum_scalar_to_str(type_py, enums.SbusI2cTriggerType)
		self._core.io.write(f'TRIGger:SBHW:I2C:TYPE {param}')

	# noinspection PyTypeChecker
	def get_access(self) -> enums.SbusIxcReadWriteBit:
		"""TRIGger:SBHW:I2C:ACCess \n
		Snippet: value: enums.SbusIxcReadWriteBit = driver.trigger.sbhw.i2C.get_access() \n
		Toggles the trigger condition between read and write access of the primary. Select Either if the transfer direction is
		not relevant for the trigger condition. \n
			:return: rwb_it_address: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:ACCess?')
		return Conversions.str_to_scalar_enum(response, enums.SbusIxcReadWriteBit)

	def set_access(self, rwb_it_address: enums.SbusIxcReadWriteBit) -> None:
		"""TRIGger:SBHW:I2C:ACCess \n
		Snippet: driver.trigger.sbhw.i2C.set_access(rwb_it_address = enums.SbusIxcReadWriteBit.EITHer) \n
		Toggles the trigger condition between read and write access of the primary. Select Either if the transfer direction is
		not relevant for the trigger condition. \n
			:param rwb_it_address: No help available
		"""
		param = Conversions.enum_scalar_to_str(rwb_it_address, enums.SbusIxcReadWriteBit)
		self._core.io.write(f'TRIGger:SBHW:I2C:ACCess {param}')

	# noinspection PyTypeChecker
	def get_amode(self) -> enums.SBusI2cAddressType:
		"""TRIGger:SBHW:I2C:AMODe \n
		Snippet: value: enums.SBusI2cAddressType = driver.trigger.sbhw.i2C.get_amode() \n
		Sets the address length to be triggered on: 7 bit or 10 bit. \n
			:return: address_type: Note that BIT7RW is the same address type as BIT7_RW.
				- BIT7 | BIT10: Enter only the seven or ten address bits in the address pattern.
				- BIT7RW | BIT7_RW: Enter seven address bits and also the read/write bit."""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:AMODe?')
		return Conversions.str_to_scalar_enum(response, enums.SBusI2cAddressType)

	def set_amode(self, address_type: enums.SBusI2cAddressType) -> None:
		"""TRIGger:SBHW:I2C:AMODe \n
		Snippet: driver.trigger.sbhw.i2C.set_amode(address_type = enums.SBusI2cAddressType.ANY) \n
		Sets the address length to be triggered on: 7 bit or 10 bit. \n
			:param address_type: Note that BIT7RW is the same address type as BIT7_RW.
				- BIT7 | BIT10: Enter only the seven or ten address bits in the address pattern.
				- BIT7RW | BIT7_RW: Enter seven address bits and also the read/write bit."""
		param = Conversions.enum_scalar_to_str(address_type, enums.SBusI2cAddressType)
		self._core.io.write(f'TRIGger:SBHW:I2C:AMODe {param}')

	def get_dw_nack(self) -> bool:
		"""TRIGger:SBHW:I2C:DWNack \n
		Snippet: value: bool = driver.trigger.sbhw.i2C.get_dw_nack() \n
		Triggers if a date acknowledge bit is missing - the addressed target does not accept the data. \n
			:return: data_write_nack: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:DWNack?')
		return Conversions.str_to_bool(response)

	def set_dw_nack(self, data_write_nack: bool) -> None:
		"""TRIGger:SBHW:I2C:DWNack \n
		Snippet: driver.trigger.sbhw.i2C.set_dw_nack(data_write_nack = False) \n
		Triggers if a date acknowledge bit is missing - the addressed target does not accept the data. \n
			:param data_write_nack: No help available
		"""
		param = Conversions.bool_to_str(data_write_nack)
		self._core.io.write(f'TRIGger:SBHW:I2C:DWNack {param}')

	def get_dr_nack(self) -> bool:
		"""TRIGger:SBHW:I2C:DRNack \n
		Snippet: value: bool = driver.trigger.sbhw.i2C.get_dr_nack() \n
		Triggers on the end of the read process when the controller reads data from the target. This NACK is sent according to
		the protocol definition, it is not an error. \n
			:return: data_read_nack: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:DRNack?')
		return Conversions.str_to_bool(response)

	def set_dr_nack(self, data_read_nack: bool) -> None:
		"""TRIGger:SBHW:I2C:DRNack \n
		Snippet: driver.trigger.sbhw.i2C.set_dr_nack(data_read_nack = False) \n
		Triggers on the end of the read process when the controller reads data from the target. This NACK is sent according to
		the protocol definition, it is not an error. \n
			:param data_read_nack: No help available
		"""
		param = Conversions.bool_to_str(data_read_nack)
		self._core.io.write(f'TRIGger:SBHW:I2C:DRNack {param}')

	def get_ad_nack(self) -> bool:
		"""TRIGger:SBHW:I2C:ADNack \n
		Snippet: value: bool = driver.trigger.sbhw.i2C.get_ad_nack() \n
		Triggers if the address acknowledge bit is missing - no target recognizes the address. \n
			:return: address_nack: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:ADNack?')
		return Conversions.str_to_bool(response)

	def set_ad_nack(self, address_nack: bool) -> None:
		"""TRIGger:SBHW:I2C:ADNack \n
		Snippet: driver.trigger.sbhw.i2C.set_ad_nack(address_nack = False) \n
		Triggers if the address acknowledge bit is missing - no target recognizes the address. \n
			:param address_nack: No help available
		"""
		param = Conversions.bool_to_str(address_nack)
		self._core.io.write(f'TRIGger:SBHW:I2C:ADNack {param}')

	def get_address(self) -> List[int]:
		"""TRIGger:SBHW:I2C:ADDRess \n
		Snippet: value: List[int] = driver.trigger.sbhw.i2C.get_address() \n
		Triggers on the specified address, or sets the start value of an address range depending on the condition set with method
		RsMxo.Trigger.Sbhw.I2C.acondition. \n
			:return: address: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:I2C:ADDRess?')
		return response

	def set_address(self, address: List[int]) -> None:
		"""TRIGger:SBHW:I2C:ADDRess \n
		Snippet: driver.trigger.sbhw.i2C.set_address(address = [1, 2, 3]) \n
		Triggers on the specified address, or sets the start value of an address range depending on the condition set with method
		RsMxo.Trigger.Sbhw.I2C.acondition. \n
			:param address: No help available
		"""
		param = Conversions.list_to_csv_str(address)
		self._core.io.write(f'TRIGger:SBHW:I2C:ADDRess {param}')

	def get_add_to(self) -> List[int]:
		"""TRIGger:SBHW:I2C:ADDTo \n
		Snippet: value: List[int] = driver.trigger.sbhw.i2C.get_add_to() \n
		Sets the end value of an address range if the condition is set to an address range with method RsMxo.Trigger.Sbhw.I2C.
		acondition. \n
			:return: address_to: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:I2C:ADDTo?')
		return response

	def set_add_to(self, address_to: List[int]) -> None:
		"""TRIGger:SBHW:I2C:ADDTo \n
		Snippet: driver.trigger.sbhw.i2C.set_add_to(address_to = [1, 2, 3]) \n
		Sets the end value of an address range if the condition is set to an address range with method RsMxo.Trigger.Sbhw.I2C.
		acondition. \n
			:param address_to: No help available
		"""
		param = Conversions.list_to_csv_str(address_to)
		self._core.io.write(f'TRIGger:SBHW:I2C:ADDTo {param}')

	def get_dmin(self) -> List[int]:
		"""TRIGger:SBHW:I2C:DMIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.i2C.get_dmin() \n
		Specifies the data bit pattern, or sets the start value of a data pattern range. Enter the bytes in MSB first bit order.
		The maximum pattern length is 64 bit. Waveform data is compared with the pattern byte-by-byte. \n
			:return: data: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:I2C:DMIN?')
		return response

	def set_dmin(self, data: List[int]) -> None:
		"""TRIGger:SBHW:I2C:DMIN \n
		Snippet: driver.trigger.sbhw.i2C.set_dmin(data = [1, 2, 3]) \n
		Specifies the data bit pattern, or sets the start value of a data pattern range. Enter the bytes in MSB first bit order.
		The maximum pattern length is 64 bit. Waveform data is compared with the pattern byte-by-byte. \n
			:param data: No help available
		"""
		param = Conversions.list_to_csv_str(data)
		self._core.io.write(f'TRIGger:SBHW:I2C:DMIN {param}')

	# noinspection PyTypeChecker
	def get_acondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:I2C:ACONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.i2C.get_acondition() \n
		Sets the operator to set a specific address or an address range. The address values are set with method RsMxo.Trigger.
		Sbhw.I2C.address and method RsMxo.Trigger.Sbhw.I2C.addTo. \n
			:return: address_operator: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:ACONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_acondition(self, address_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:I2C:ACONdition \n
		Snippet: driver.trigger.sbhw.i2C.set_acondition(address_operator = enums.OperatorB.EQUal) \n
		Sets the operator to set a specific address or an address range. The address values are set with method RsMxo.Trigger.
		Sbhw.I2C.address and method RsMxo.Trigger.Sbhw.I2C.addTo. \n
			:param address_operator: No help available
		"""
		param = Conversions.enum_scalar_to_str(address_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:I2C:ACONdition {param}')

	# noinspection PyTypeChecker
	def get_dcondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:I2C:DCONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.i2C.get_dcondition() \n
		Sets the operator to set a specific data value or a data range. \n
			:return: data_operator: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:DCONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_dcondition(self, data_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:I2C:DCONdition \n
		Snippet: driver.trigger.sbhw.i2C.set_dcondition(data_operator = enums.OperatorB.EQUal) \n
		Sets the operator to set a specific data value or a data range. \n
			:param data_operator: No help available
		"""
		param = Conversions.enum_scalar_to_str(data_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:I2C:DCONdition {param}')

	def get_dposition(self) -> int:
		"""TRIGger:SBHW:I2C:DPOSition \n
		Snippet: value: int = driver.trigger.sbhw.i2C.get_dposition() \n
		Sets the number of data bytes to be skipped after the address. \n
			:return: data_position: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:I2C:DPOSition?')
		return Conversions.str_to_int(response)

	def set_dposition(self, data_position: int) -> None:
		"""TRIGger:SBHW:I2C:DPOSition \n
		Snippet: driver.trigger.sbhw.i2C.set_dposition(data_position = 1) \n
		Sets the number of data bytes to be skipped after the address. \n
			:param data_position: No help available
		"""
		param = Conversions.decimal_value_to_str(data_position)
		self._core.io.write(f'TRIGger:SBHW:I2C:DPOSition {param}')
