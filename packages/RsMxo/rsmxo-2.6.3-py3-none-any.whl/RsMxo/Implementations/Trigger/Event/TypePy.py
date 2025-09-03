from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, type_py: enums.TriggerEventType, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:TYPE \n
		Snippet: driver.trigger.event.typePy.set(type_py = enums.TriggerEventType.ANEDge, evnt = repcap.Evnt.Default) \n
		Selects the trigger type. In a trigger sequence, the trigger type is set for each condition. \n
			:param type_py: ANEDge = analog edge trigger is the only trigger type if the extern trigger source is used. For SETHold, also DATatoclock can be used.
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.TriggerEventType)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.TriggerEventType:
		"""TRIGger:EVENt<*>:TYPE \n
		Snippet: value: enums.TriggerEventType = driver.trigger.event.typePy.get(evnt = repcap.Evnt.Default) \n
		Selects the trigger type. In a trigger sequence, the trigger type is set for each condition. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: type_py: ANEDge = analog edge trigger is the only trigger type if the extern trigger source is used. For SETHold, also DATatoclock can be used."""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerEventType)
