from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SpiCls:
	"""Spi commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("spi", core, parent)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.SbusSpiTriggerType:
		"""TRIGger:SBHW:SPI:TYPE \n
		Snippet: value: enums.SbusSpiTriggerType = driver.trigger.sbhw.spi.get_type_py() \n
		Selects the trigger type for SPI analysis. \n
			:return: type_py:
				- FRSTart: Triggers on the beginning of the frame.
				- FRENd: Triggers on the end of the frame.
				- MOSI: Triggers on a specified data pattern in that is expected on the MOSI line.
				- MISO: Triggers on a specified data pattern in that is expected on the MISO line."""
		response = self._core.io.query_str('TRIGger:SBHW:SPI:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSpiTriggerType)

	def set_type_py(self, type_py: enums.SbusSpiTriggerType) -> None:
		"""TRIGger:SBHW:SPI:TYPE \n
		Snippet: driver.trigger.sbhw.spi.set_type_py(type_py = enums.SbusSpiTriggerType.FRENd) \n
		Selects the trigger type for SPI analysis. \n
			:param type_py:
				- FRSTart: Triggers on the beginning of the frame.
				- FRENd: Triggers on the end of the frame.
				- MOSI: Triggers on a specified data pattern in that is expected on the MOSI line.
				- MISO: Triggers on a specified data pattern in that is expected on the MISO line."""
		param = Conversions.enum_scalar_to_str(type_py, enums.SbusSpiTriggerType)
		self._core.io.write(f'TRIGger:SBHW:SPI:TYPE {param}')

	def get_dmin_pattern(self) -> List[int]:
		"""TRIGger:SBHW:SPI:DMINpattern \n
		Snippet: value: List[int] = driver.trigger.sbhw.spi.get_dmin_pattern() \n
		Specifies a data bit pattern, or sets the start value of a pattern range. \n
			:return: data_pattern: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:SPI:DMINpattern?')
		return response

	def set_dmin_pattern(self, data_pattern: List[int]) -> None:
		"""TRIGger:SBHW:SPI:DMINpattern \n
		Snippet: driver.trigger.sbhw.spi.set_dmin_pattern(data_pattern = [1, 2, 3]) \n
		Specifies a data bit pattern, or sets the start value of a pattern range. \n
			:param data_pattern: No help available
		"""
		param = Conversions.list_to_csv_str(data_pattern)
		self._core.io.write(f'TRIGger:SBHW:SPI:DMINpattern {param}')

	# noinspection PyTypeChecker
	def get_palignment(self) -> enums.DataAlignment:
		"""TRIGger:SBHW:SPI:PALignment \n
		Snippet: value: enums.DataAlignment = driver.trigger.sbhw.spi.get_palignment() \n
		Defines how the specified data pattern is searched. \n
			:return: data_alignment:
				- WORD: The pattern is matched only at word boundaries.
				- BIT: Bit-by-bit: the pattern can start at any position in the message."""
		response = self._core.io.query_str('TRIGger:SBHW:SPI:PALignment?')
		return Conversions.str_to_scalar_enum(response, enums.DataAlignment)

	def set_palignment(self, data_alignment: enums.DataAlignment) -> None:
		"""TRIGger:SBHW:SPI:PALignment \n
		Snippet: driver.trigger.sbhw.spi.set_palignment(data_alignment = enums.DataAlignment.BIT) \n
		Defines how the specified data pattern is searched. \n
			:param data_alignment:
				- WORD: The pattern is matched only at word boundaries.
				- BIT: Bit-by-bit: the pattern can start at any position in the message."""
		param = Conversions.enum_scalar_to_str(data_alignment, enums.DataAlignment)
		self._core.io.write(f'TRIGger:SBHW:SPI:PALignment {param}')

	# noinspection PyTypeChecker
	def get_fcondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:SPI:FCONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.spi.get_fcondition() \n
		Selects the operator for the MISO and MOSI pattern. \n
			:return: data_operator: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:SPI:FCONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_fcondition(self, data_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:SPI:FCONdition \n
		Snippet: driver.trigger.sbhw.spi.set_fcondition(data_operator = enums.OperatorB.EQUal) \n
		Selects the operator for the MISO and MOSI pattern. \n
			:param data_operator: No help available
		"""
		param = Conversions.enum_scalar_to_str(data_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:SPI:FCONdition {param}')

	def get_dposition(self) -> int:
		"""TRIGger:SBHW:SPI:DPOSition \n
		Snippet: value: int = driver.trigger.sbhw.spi.get_dposition() \n
		Sets the number of bits or words to be ignored before the first bit or word of interest. The effect is defined by method
		RsMxo.Trigger.Sbhw.Spi.palignment. \n
			:return: data_position: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:SPI:DPOSition?')
		return Conversions.str_to_int(response)

	def set_dposition(self, data_position: int) -> None:
		"""TRIGger:SBHW:SPI:DPOSition \n
		Snippet: driver.trigger.sbhw.spi.set_dposition(data_position = 1) \n
		Sets the number of bits or words to be ignored before the first bit or word of interest. The effect is defined by method
		RsMxo.Trigger.Sbhw.Spi.palignment. \n
			:param data_position: No help available
		"""
		param = Conversions.decimal_value_to_str(data_position)
		self._core.io.write(f'TRIGger:SBHW:SPI:DPOSition {param}')
