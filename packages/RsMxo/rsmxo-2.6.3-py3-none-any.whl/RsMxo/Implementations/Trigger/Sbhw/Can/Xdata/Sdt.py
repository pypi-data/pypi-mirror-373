from typing import List

from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SdtCls:
	"""Sdt commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sdt", core, parent)

	# noinspection PyTypeChecker
	def get_condition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:CAN:XDATa:SDT:CONDition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.can.xdata.sdt.get_condition() \n
		Sets the comparison condition for the service data unit type to a specific value or a range. \n
			:return: sdt_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one pattern to be set with TRIGger:SBHW:CAN:XDATa:SDT:MIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:XDATa:SDT:MIN and TRIGger:SBHW:CAN:XDATa:SDT:MAX."""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:XDATa:SDT:CONDition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_condition(self, sdt_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:CAN:XDATa:SDT:CONDition \n
		Snippet: driver.trigger.sbhw.can.xdata.sdt.set_condition(sdt_operator = enums.OperatorB.EQUal) \n
		Sets the comparison condition for the service data unit type to a specific value or a range. \n
			:param sdt_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one pattern to be set with TRIGger:SBHW:CAN:XDATa:SDT:MIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:XDATa:SDT:MIN and TRIGger:SBHW:CAN:XDATa:SDT:MAX."""
		param = Conversions.enum_scalar_to_str(sdt_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:SDT:CONDition {param}')

	def get_min(self) -> List[int]:
		"""TRIGger:SBHW:CAN:XDATa:SDT:MIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.xdata.sdt.get_min() \n
		Specifies a service data unit type pattern, or sets the start value of a range. \n
			:return: sdt_pattern: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:XDATa:SDT:MIN?')
		return response

	def set_min(self, sdt_pattern: List[int]) -> None:
		"""TRIGger:SBHW:CAN:XDATa:SDT:MIN \n
		Snippet: driver.trigger.sbhw.can.xdata.sdt.set_min(sdt_pattern = [1, 2, 3]) \n
		Specifies a service data unit type pattern, or sets the start value of a range. \n
			:param sdt_pattern: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(sdt_pattern)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:SDT:MIN {param}')

	def get_max(self) -> List[int]:
		"""TRIGger:SBHW:CAN:XDATa:SDT:MAX \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.xdata.sdt.get_max() \n
		Sets the end value of a service data unit type range if method RsMxo.Trigger.Sbhw.Can.Xdata.Sdt.condition is set to
		INRange or OORange. \n
			:return: sdt_pattern_to: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:XDATa:SDT:MAX?')
		return response

	def set_max(self, sdt_pattern_to: List[int]) -> None:
		"""TRIGger:SBHW:CAN:XDATa:SDT:MAX \n
		Snippet: driver.trigger.sbhw.can.xdata.sdt.set_max(sdt_pattern_to = [1, 2, 3]) \n
		Sets the end value of a service data unit type range if method RsMxo.Trigger.Sbhw.Can.Xdata.Sdt.condition is set to
		INRange or OORange. \n
			:param sdt_pattern_to: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(sdt_pattern_to)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:SDT:MAX {param}')
