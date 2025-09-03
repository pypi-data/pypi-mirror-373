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

	def set(self, hlx: enums.Hlx, evnt=repcap.Evnt.Default, channelDigital=repcap.ChannelDigital.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:QUALify:DIGital:CHAN<*>:HLX \n
		Snippet: driver.trigger.event.pattern.qualify.digital.chan.hlx.set(hlx = enums.Hlx.DONTcare, evnt = repcap.Evnt.Default, channelDigital = repcap.ChannelDigital.Default) \n
		Sets the required state for each digital channel that is used for triggering. \n
			:param hlx: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param channelDigital: optional repeated capability selector. Default value: DigCh1 (settable in the interface 'Chan')
		"""
		param = Conversions.enum_scalar_to_str(hlx, enums.Hlx)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		channelDigital_cmd_val = self._cmd_group.get_repcap_cmd_value(channelDigital, repcap.ChannelDigital)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:DIGital:CHAN{channelDigital_cmd_val}:HLX {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default, channelDigital=repcap.ChannelDigital.Default) -> enums.Hlx:
		"""TRIGger:EVENt<*>:PATTern:QUALify:DIGital:CHAN<*>:HLX \n
		Snippet: value: enums.Hlx = driver.trigger.event.pattern.qualify.digital.chan.hlx.get(evnt = repcap.Evnt.Default, channelDigital = repcap.ChannelDigital.Default) \n
		Sets the required state for each digital channel that is used for triggering. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param channelDigital: optional repeated capability selector. Default value: DigCh1 (settable in the interface 'Chan')
			:return: hlx: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		channelDigital_cmd_val = self._cmd_group.get_repcap_cmd_value(channelDigital, repcap.ChannelDigital)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:DIGital:CHAN{channelDigital_cmd_val}:HLX?')
		return Conversions.str_to_scalar_enum(response, enums.Hlx)
