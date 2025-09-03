from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:QUALify:STATe \n
		Snippet: driver.trigger.event.pattern.qualify.state.set(state = False, evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param state: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.bool_to_str(state)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:STATe {param}')

	def get(self, evnt=repcap.Evnt.Default) -> bool:
		"""TRIGger:EVENt<*>:PATTern:QUALify:STATe \n
		Snippet: value: bool = driver.trigger.event.pattern.qualify.state.get(evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: state: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:STATe?')
		return Conversions.str_to_bool(response)
