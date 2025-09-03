from typing import List

from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AfCls:
	"""Af commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("af", core, parent)

	# noinspection PyTypeChecker
	def get_condition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:CAN:XDATa:AF:CONDition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.can.xdata.af.get_condition() \n
		Sets the comparison condition for the acceptance field to a specific value or a range. \n
			:return: af_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one pattern to be set with TRIGger:SBHW:CAN:XDATa:AF:MIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:XDATa:AF:MIN and TRIGger:SBHW:CAN:XDATa:AF:MAX."""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:XDATa:AF:CONDition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_condition(self, af_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:CAN:XDATa:AF:CONDition \n
		Snippet: driver.trigger.sbhw.can.xdata.af.set_condition(af_operator = enums.OperatorB.EQUal) \n
		Sets the comparison condition for the acceptance field to a specific value or a range. \n
			:param af_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one pattern to be set with TRIGger:SBHW:CAN:XDATa:AF:MIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:XDATa:AF:MIN and TRIGger:SBHW:CAN:XDATa:AF:MAX."""
		param = Conversions.enum_scalar_to_str(af_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:AF:CONDition {param}')

	def get_min(self) -> List[int]:
		"""TRIGger:SBHW:CAN:XDATa:AF:MIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.xdata.af.get_min() \n
		Specifies an acceptance field pattern, or sets the start value of a range. \n
			:return: af_pattern: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:XDATa:AF:MIN?')
		return response

	def set_min(self, af_pattern: List[int]) -> None:
		"""TRIGger:SBHW:CAN:XDATa:AF:MIN \n
		Snippet: driver.trigger.sbhw.can.xdata.af.set_min(af_pattern = [1, 2, 3]) \n
		Specifies an acceptance field pattern, or sets the start value of a range. \n
			:param af_pattern: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(af_pattern)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:AF:MIN {param}')

	def get_max(self) -> List[int]:
		"""TRIGger:SBHW:CAN:XDATa:AF:MAX \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.xdata.af.get_max() \n
		Sets the end value of an acceptance field if method RsMxo.Trigger.Sbhw.Can.Xdata.Af.condition is set to INRange or
		OORange. \n
			:return: af_pattern_to: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:XDATa:AF:MAX?')
		return response

	def set_max(self, af_pattern_to: List[int]) -> None:
		"""TRIGger:SBHW:CAN:XDATa:AF:MAX \n
		Snippet: driver.trigger.sbhw.can.xdata.af.set_max(af_pattern_to = [1, 2, 3]) \n
		Sets the end value of an acceptance field if method RsMxo.Trigger.Sbhw.Can.Xdata.Af.condition is set to INRange or
		OORange. \n
			:param af_pattern_to: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(af_pattern_to)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:AF:MAX {param}')
