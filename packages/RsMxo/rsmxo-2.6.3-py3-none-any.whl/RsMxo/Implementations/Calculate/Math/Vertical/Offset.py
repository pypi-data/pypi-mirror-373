from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OffsetCls:
	"""Offset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	def set(self, vertical_offset: float, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:VERTical:OFFSet \n
		Snippet: driver.calculate.math.vertical.offset.set(vertical_offset = 1.0, math = repcap.Math.Default) \n
		Sets a voltage offset to adjust the vertical position of the math function on the screen. Negative values move the
		waveform up, positive values move it down. \n
			:param vertical_offset: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.decimal_value_to_str(vertical_offset)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:VERTical:OFFSet {param}')

	def get(self, math=repcap.Math.Default) -> float:
		"""CALCulate:MATH<*>:VERTical:OFFSet \n
		Snippet: value: float = driver.calculate.math.vertical.offset.get(math = repcap.Math.Default) \n
		Sets a voltage offset to adjust the vertical position of the math function on the screen. Negative values move the
		waveform up, positive values move it down. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: vertical_offset: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:VERTical:OFFSet?')
		return Conversions.str_to_float(response)
