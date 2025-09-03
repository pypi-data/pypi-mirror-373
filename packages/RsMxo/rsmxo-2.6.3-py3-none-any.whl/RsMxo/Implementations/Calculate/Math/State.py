from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, first: bool, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:STATe \n
		Snippet: driver.calculate.math.state.set(first = False, math = repcap.Math.Default) \n
		Activates the selected Math channel and displays the defined math waveforms. \n
			:param first: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.bool_to_str(first)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:STATe {param}')

	def get(self, math=repcap.Math.Default) -> bool:
		"""CALCulate:MATH<*>:STATe \n
		Snippet: value: bool = driver.calculate.math.state.get(math = repcap.Math.Default) \n
		Activates the selected Math channel and displays the defined math waveforms. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: first: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
