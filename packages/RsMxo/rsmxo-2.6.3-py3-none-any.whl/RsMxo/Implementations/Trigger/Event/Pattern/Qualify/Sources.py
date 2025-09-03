from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourcesCls:
	"""Sources commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sources", core, parent)

	def set(self, state_sources: enums.TriggerPatternSource, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:QUALify:SOURces \n
		Snippet: driver.trigger.event.pattern.qualify.sources.set(state_sources = enums.TriggerPatternSource.AAD, evnt = repcap.Evnt.Default) \n
		Selects if the source of the trigger for the pattern type is an analog or digital channel. \n
			:param state_sources: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(state_sources, enums.TriggerPatternSource)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:SOURces {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.TriggerPatternSource:
		"""TRIGger:EVENt<*>:PATTern:QUALify:SOURces \n
		Snippet: value: enums.TriggerPatternSource = driver.trigger.event.pattern.qualify.sources.get(evnt = repcap.Evnt.Default) \n
		Selects if the source of the trigger for the pattern type is an analog or digital channel. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: state_sources: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:QUALify:SOURces?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerPatternSource)
