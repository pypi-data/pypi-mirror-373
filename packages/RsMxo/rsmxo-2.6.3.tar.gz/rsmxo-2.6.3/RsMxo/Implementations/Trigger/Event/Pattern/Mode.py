from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, mode: enums.TriggerPatternMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:MODE \n
		Snippet: driver.trigger.event.pattern.mode.set(mode = enums.TriggerPatternMode.OFF, evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param mode: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.TriggerPatternMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.TriggerPatternMode:
		"""TRIGger:EVENt<*>:PATTern:MODE \n
		Snippet: value: enums.TriggerPatternMode = driver.trigger.event.pattern.mode.get(evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: mode: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerPatternMode)
