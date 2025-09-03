from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EventCls:
	"""Event commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("event", core, parent)

	def set(self, value: bool, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:PPSupply:STATus[:EVENt] \n
		Snippet: driver.channel.ppSupply.status.event.set(value = False, channel = repcap.Channel.Default) \n
		Returns the contents of the EVENt part of the status register to check if an event has occurred since the last reading.
		Reading an EVENt register deletes its contents. \n
			:param value: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.bool_to_str(value)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:PPSupply:STATus:EVENt {param}')

	def get(self, channel=repcap.Channel.Default) -> bool:
		"""CHANnel<*>:PPSupply:STATus[:EVENt] \n
		Snippet: value: bool = driver.channel.ppSupply.status.event.get(channel = repcap.Channel.Default) \n
		Returns the contents of the EVENt part of the status register to check if an event has occurred since the last reading.
		Reading an EVENt register deletes its contents. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: value: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:PPSupply:STATus:EVENt?')
		return Conversions.str_to_bool(response)
