from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImpedanceCls:
	"""Impedance commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("impedance", core, parent)

	def set(self, impedance: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:IMPedance \n
		Snippet: driver.channel.impedance.set(impedance = 1.0, channel = repcap.Channel.Default) \n
		Sets the impedance of the connected probe for power calculations and measurements. \n
			:param impedance: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.decimal_value_to_str(impedance)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:IMPedance {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:IMPedance \n
		Snippet: value: float = driver.channel.impedance.get(channel = repcap.Channel.Default) \n
		Sets the impedance of the connected probe for power calculations and measurements. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: impedance: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:IMPedance?')
		return Conversions.str_to_float(response)
