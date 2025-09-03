from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GtwdithCls:
	"""Gtwdith commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gtwdith", core, parent)

	def set(self, glitch_filter_width: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPMI:GTWDith \n
		Snippet: driver.sbus.spmi.gtwdith.set(glitch_filter_width = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the glitch width. Any signal transitions with a duration smaller than this value will be considered a glitch and
		filtered out. This is available, if method RsMxo.Sbus.Spmi.GtchEnable.set is set to ON. \n
			:param glitch_filter_width: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(glitch_filter_width)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPMI:GTWDith {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:SPMI:GTWDith \n
		Snippet: value: float = driver.sbus.spmi.gtwdith.get(serialBus = repcap.SerialBus.Default) \n
		Sets the glitch width. Any signal transitions with a duration smaller than this value will be considered a glitch and
		filtered out. This is available, if method RsMxo.Sbus.Spmi.GtchEnable.set is set to ON. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: glitch_filter_width: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPMI:GTWDith?')
		return Conversions.str_to_float(response)
