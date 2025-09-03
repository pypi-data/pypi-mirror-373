from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AdLogicCls:
	"""AdLogic commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("adLogic", core, parent)

	def set(self, ad_logic: enums.AdLogic, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:QUALify:ADLogic \n
		Snippet: driver.trigger.event.pattern.qualify.adLogic.set(ad_logic = enums.AdLogic.AND, evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param ad_logic: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(ad_logic, enums.AdLogic)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:ADLogic {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.AdLogic:
		"""TRIGger:EVENt<*>:PATTern:QUALify:ADLogic \n
		Snippet: value: enums.AdLogic = driver.trigger.event.pattern.qualify.adLogic.get(evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: ad_logic: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:ADLogic?')
		return Conversions.str_to_scalar_enum(response, enums.AdLogic)
