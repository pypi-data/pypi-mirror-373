from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GtchEnableCls:
	"""GtchEnable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gtchEnable", core, parent)

	def set(self, use_glitch_filter: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPMI:GTCHenable \n
		Snippet: driver.sbus.spmi.gtchEnable.set(use_glitch_filter = False, serialBus = repcap.SerialBus.Default) \n
		Enables the glitch filter. A glitch filter can help to filter out short-duration voltage spikes/ glitches that can occur
		on the communication line. You can set the glitch filter width with method RsMxo.Sbus.Spmi.Gtwdith.set. \n
			:param use_glitch_filter: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(use_glitch_filter)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPMI:GTCHenable {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:SPMI:GTCHenable \n
		Snippet: value: bool = driver.sbus.spmi.gtchEnable.get(serialBus = repcap.SerialBus.Default) \n
		Enables the glitch filter. A glitch filter can help to filter out short-duration voltage spikes/ glitches that can occur
		on the communication line. You can set the glitch filter width with method RsMxo.Sbus.Spmi.Gtwdith.set. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: use_glitch_filter: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPMI:GTCHenable?')
		return Conversions.str_to_bool(response)
