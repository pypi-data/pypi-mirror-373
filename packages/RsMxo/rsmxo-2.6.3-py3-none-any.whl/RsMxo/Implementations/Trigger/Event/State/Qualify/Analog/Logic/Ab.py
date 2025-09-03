from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal import Conversions
from ........ import enums
from ........ import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AbCls:
	"""Ab commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ab", core, parent)

	def set(self, ab: enums.AdLogic, evnt=repcap.Evnt.Default, logic=repcap.Logic.Default) -> None:
		"""TRIGger:EVENt<*>:STATe:QUALify:ANALog:LOGic<*>:AB \n
		Snippet: driver.trigger.event.state.qualify.analog.logic.ab.set(ab = enums.AdLogic.AND, evnt = repcap.Evnt.Default, logic = repcap.Logic.Default) \n
		No command help available \n
			:param ab: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param logic: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Logic')
		"""
		param = Conversions.enum_scalar_to_str(ab, enums.AdLogic)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		logic_cmd_val = self._cmd_group.get_repcap_cmd_value(logic, repcap.Logic)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:STATe:QUALify:ANALog:LOGic{logic_cmd_val}:AB {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default, logic=repcap.Logic.Default) -> enums.AdLogic:
		"""TRIGger:EVENt<*>:STATe:QUALify:ANALog:LOGic<*>:AB \n
		Snippet: value: enums.AdLogic = driver.trigger.event.state.qualify.analog.logic.ab.get(evnt = repcap.Evnt.Default, logic = repcap.Logic.Default) \n
		No command help available \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param logic: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Logic')
			:return: ab: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		logic_cmd_val = self._cmd_group.get_repcap_cmd_value(logic, repcap.Logic)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:STATe:QUALify:ANALog:LOGic{logic_cmd_val}:AB?')
		return Conversions.str_to_scalar_enum(response, enums.AdLogic)
