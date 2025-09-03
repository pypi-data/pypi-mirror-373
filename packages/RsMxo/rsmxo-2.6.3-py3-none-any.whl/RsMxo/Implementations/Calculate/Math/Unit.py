from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UnitCls:
	"""Unit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("unit", core, parent)

	def set(self, user_unit: str, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:UNIT \n
		Snippet: driver.calculate.math.unit.set(user_unit = 'abc', math = repcap.Math.Default) \n
		Sets a user-defined unit for the math operation. \n
			:param user_unit: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.value_to_quoted_str(user_unit)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:UNIT {param}')

	def get(self, math=repcap.Math.Default) -> str:
		"""CALCulate:MATH<*>:UNIT \n
		Snippet: value: str = driver.calculate.math.unit.get(math = repcap.Math.Default) \n
		Sets a user-defined unit for the math operation. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: user_unit: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:UNIT?')
		return trim_str_response(response)
