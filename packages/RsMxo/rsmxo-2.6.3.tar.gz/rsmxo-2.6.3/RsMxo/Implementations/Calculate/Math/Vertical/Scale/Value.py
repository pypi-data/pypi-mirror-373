from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, vertical_scale: float, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:VERTical:SCALe[:VALue] \n
		Snippet: driver.calculate.math.vertical.scale.value.set(vertical_scale = 1.0, math = repcap.Math.Default) \n
		Sets the scale of the y-axis in the math function diagram. The value is defined as '<unit> per division', e.g. 50 mV/div.
		In this case, the horizontal grid lines are displayed in intervals of 50 mV. \n
			:param vertical_scale: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.decimal_value_to_str(vertical_scale)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:VERTical:SCALe:VALue {param}')

	def get(self, math=repcap.Math.Default) -> float:
		"""CALCulate:MATH<*>:VERTical:SCALe[:VALue] \n
		Snippet: value: float = driver.calculate.math.vertical.scale.value.get(math = repcap.Math.Default) \n
		Sets the scale of the y-axis in the math function diagram. The value is defined as '<unit> per division', e.g. 50 mV/div.
		In this case, the horizontal grid lines are displayed in intervals of 50 mV. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: vertical_scale: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:VERTical:SCALe:VALue?')
		return Conversions.str_to_float(response)
