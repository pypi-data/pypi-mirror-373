from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, source_detailed: enums.SourceDetailed, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SOURce \n
		Snippet: driver.trigger.event.source.set(source_detailed = enums.SourceDetailed.C1, evnt = repcap.Evnt.Default) \n
		Selects the source of the trigger signal for the selected trigger event. The trigger source works even if it is not
		displayed in a diagram. Available sources depend on the trigger sequence setting. If you trigger on a single event, all
		inputs can be used as trigger source. If you trigger on a sequence, only analog channels can be set as trigger source. \n
			:param source_detailed:
				- C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8: Available for single event and all events in a trigger sequence
				- EXTernanalog | LINE | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 | D14 | D15 | SBUS1 | SBUS2 | SBUS3 | SBUS4: Available for single event (EVENt1)
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')"""
		param = Conversions.enum_scalar_to_str(source_detailed, enums.SourceDetailed)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.SourceDetailed:
		"""TRIGger:EVENt<*>:SOURce \n
		Snippet: value: enums.SourceDetailed = driver.trigger.event.source.get(evnt = repcap.Evnt.Default) \n
		Selects the source of the trigger signal for the selected trigger event. The trigger source works even if it is not
		displayed in a diagram. Available sources depend on the trigger sequence setting. If you trigger on a single event, all
		inputs can be used as trigger source. If you trigger on a sequence, only analog channels can be set as trigger source. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: source_detailed:
				- C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8: Available for single event and all events in a trigger sequence
				- EXTernanalog | LINE | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 | D14 | D15 | SBUS1 | SBUS2 | SBUS3 | SBUS4: Available for single event (EVENt1) """
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.SourceDetailed)
