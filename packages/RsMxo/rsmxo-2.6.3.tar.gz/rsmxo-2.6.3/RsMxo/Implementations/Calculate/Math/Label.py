from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def set(self, label: str, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:LABel \n
		Snippet: driver.calculate.math.label.set(label = 'abc', math = repcap.Math.Default) \n
		Defines a label for the selected math waveform. \n
			:param label: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.value_to_quoted_str(label)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:LABel {param}')

	def get(self, math=repcap.Math.Default) -> str:
		"""CALCulate:MATH<*>:LABel \n
		Snippet: value: str = driver.calculate.math.label.get(math = repcap.Math.Default) \n
		Defines a label for the selected math waveform. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: label: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:LABel?')
		return trim_str_response(response)
