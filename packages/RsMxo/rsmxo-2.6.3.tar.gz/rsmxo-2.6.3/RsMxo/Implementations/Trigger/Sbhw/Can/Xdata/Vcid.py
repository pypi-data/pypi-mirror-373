from typing import List

from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VcidCls:
	"""Vcid commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("vcid", core, parent)

	# noinspection PyTypeChecker
	def get_condition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:CAN:XDATa:VCID:CONDition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.can.xdata.vcid.get_condition() \n
		Sets the comparison condition for the VCID to a specific value or a range. \n
			:return: vcid_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one pattern to be set with TRIGger:SBHW:CAN:XDATa:VCID:MIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:XDATa:VCID:MIN and TRIGger:SBHW:CAN:XDATa:VCID:MAX."""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:XDATa:VCID:CONDition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_condition(self, vcid_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:CAN:XDATa:VCID:CONDition \n
		Snippet: driver.trigger.sbhw.can.xdata.vcid.set_condition(vcid_operator = enums.OperatorB.EQUal) \n
		Sets the comparison condition for the VCID to a specific value or a range. \n
			:param vcid_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one pattern to be set with TRIGger:SBHW:CAN:XDATa:VCID:MIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:XDATa:VCID:MIN and TRIGger:SBHW:CAN:XDATa:VCID:MAX."""
		param = Conversions.enum_scalar_to_str(vcid_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:VCID:CONDition {param}')

	def get_min(self) -> List[int]:
		"""TRIGger:SBHW:CAN:XDATa:VCID:MIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.xdata.vcid.get_min() \n
		Specifies a VCID pattern, or sets the start value of a range. \n
			:return: vcid_pattern: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:XDATa:VCID:MIN?')
		return response

	def set_min(self, vcid_pattern: List[int]) -> None:
		"""TRIGger:SBHW:CAN:XDATa:VCID:MIN \n
		Snippet: driver.trigger.sbhw.can.xdata.vcid.set_min(vcid_pattern = [1, 2, 3]) \n
		Specifies a VCID pattern, or sets the start value of a range. \n
			:param vcid_pattern: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(vcid_pattern)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:VCID:MIN {param}')

	def get_max(self) -> List[int]:
		"""TRIGger:SBHW:CAN:XDATa:VCID:MAX \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.xdata.vcid.get_max() \n
		Sets the end value of a VCID range if method RsMxo.Trigger.Sbhw.Can.Xdata.Vcid.condition is set to INRange or OORange. \n
			:return: vcid_pattern_to: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:XDATa:VCID:MAX?')
		return response

	def set_max(self, vcid_pattern_to: List[int]) -> None:
		"""TRIGger:SBHW:CAN:XDATa:VCID:MAX \n
		Snippet: driver.trigger.sbhw.can.xdata.vcid.set_max(vcid_pattern_to = [1, 2, 3]) \n
		Sets the end value of a VCID range if method RsMxo.Trigger.Sbhw.Can.Xdata.Vcid.condition is set to INRange or OORange. \n
			:param vcid_pattern_to: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(vcid_pattern_to)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:VCID:MAX {param}')
