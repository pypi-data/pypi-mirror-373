from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LogicCls:
	"""Logic commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("logic", core, parent)

	def set(self, logic: enums.AdLogic, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:QUALify:DIGital:LOGic \n
		Snippet: driver.trigger.event.pattern.qualify.digital.logic.set(logic = enums.AdLogic.AND, evnt = repcap.Evnt.Default) \n
		Defines the logic combination of the channels and their states. \n
			:param logic: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(logic, enums.AdLogic)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:DIGital:LOGic {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.AdLogic:
		"""TRIGger:EVENt<*>:PATTern:QUALify:DIGital:LOGic \n
		Snippet: value: enums.AdLogic = driver.trigger.event.pattern.qualify.digital.logic.get(evnt = repcap.Evnt.Default) \n
		Defines the logic combination of the channels and their states. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: logic: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:DIGital:LOGic?')
		return Conversions.str_to_scalar_enum(response, enums.AdLogic)
