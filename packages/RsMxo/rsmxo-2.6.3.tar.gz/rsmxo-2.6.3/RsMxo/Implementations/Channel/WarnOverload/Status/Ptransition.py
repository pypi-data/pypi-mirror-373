from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PtransitionCls:
	"""Ptransition commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ptransition", core, parent)

	def set(self, value: bool, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:WARNoverload:STATus:PTRansition \n
		Snippet: driver.channel.warnOverload.status.ptransition.set(value = False, channel = repcap.Channel.Default) \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param value: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.bool_to_str(value)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:WARNoverload:STATus:PTRansition {param}')

	def get(self, channel=repcap.Channel.Default) -> bool:
		"""CHANnel<*>:WARNoverload:STATus:PTRansition \n
		Snippet: value: bool = driver.channel.warnOverload.status.ptransition.get(channel = repcap.Channel.Default) \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: value: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:WARNoverload:STATus:PTRansition?')
		return Conversions.str_to_bool(response)
