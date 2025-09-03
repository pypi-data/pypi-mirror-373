from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WidthCls:
	"""Width commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("width", core, parent)

	def set(self, min_gap_width: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:I3C:MINGap:WIDTh \n
		Snippet: driver.sbus.i3C.minGap.width.set(min_gap_width = 1.0, serialBus = repcap.SerialBus.Default) \n
		Specifies the minimum duration of the gap. Available, if method RsMxo.Sbus.I3C.MinGap.Select.set is set to ON. \n
			:param min_gap_width: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(min_gap_width)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:I3C:MINGap:WIDTh {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:I3C:MINGap:WIDTh \n
		Snippet: value: float = driver.sbus.i3C.minGap.width.get(serialBus = repcap.SerialBus.Default) \n
		Specifies the minimum duration of the gap. Available, if method RsMxo.Sbus.I3C.MinGap.Select.set is set to ON. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: min_gap_width: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I3C:MINGap:WIDTh?')
		return Conversions.str_to_float(response)
