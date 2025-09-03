from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FilFrequencyCls:
	"""FilFrequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("filFrequency", core, parent)

	def set(self, filter_design_freq: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:FILFrequency \n
		Snippet: driver.channel.filFrequency.set(filter_design_freq = 1.0, channel = repcap.Channel.Default) \n
		No command help available \n
			:param filter_design_freq: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.decimal_value_to_str(filter_design_freq)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:FILFrequency {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:FILFrequency \n
		Snippet: value: float = driver.channel.filFrequency.get(channel = repcap.Channel.Default) \n
		No command help available \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: filter_design_freq: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:FILFrequency?')
		return Conversions.str_to_float(response)
