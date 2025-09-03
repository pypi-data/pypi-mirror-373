from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal import Conversions
from ........ import enums
from ........ import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HlxCls:
	"""Hlx commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hlx", core, parent)

	def set(self, hlx: enums.Hlx, evnt=repcap.Evnt.Default, channel=repcap.Channel.Default) -> None:
		"""TRIGger:EVENt<*>:STATe:QUALify:ANALog:CHAN<*>:HLX \n
		Snippet: driver.trigger.event.state.qualify.analog.chan.hlx.set(hlx = enums.Hlx.DONTcare, evnt = repcap.Evnt.Default, channel = repcap.Channel.Default) \n
		Set the state for each channel. For the state trigger, the clock source is indicated and does not get a state. \n
			:param hlx: State of the individual channels
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Chan')
		"""
		param = Conversions.enum_scalar_to_str(hlx, enums.Hlx)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:STATe:QUALify:ANALog:CHAN{channel_cmd_val}:HLX {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default, channel=repcap.Channel.Default) -> enums.Hlx:
		"""TRIGger:EVENt<*>:STATe:QUALify:ANALog:CHAN<*>:HLX \n
		Snippet: value: enums.Hlx = driver.trigger.event.state.qualify.analog.chan.hlx.get(evnt = repcap.Evnt.Default, channel = repcap.Channel.Default) \n
		Set the state for each channel. For the state trigger, the clock source is indicated and does not get a state. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Chan')
			:return: hlx: State of the individual channels"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:STATe:QUALify:ANALog:CHAN{channel_cmd_val}:HLX?')
		return Conversions.str_to_scalar_enum(response, enums.Hlx)
