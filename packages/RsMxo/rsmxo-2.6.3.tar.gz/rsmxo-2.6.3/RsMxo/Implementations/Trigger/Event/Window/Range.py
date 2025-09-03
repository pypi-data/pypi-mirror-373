from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RangeCls:
	"""Range commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("range", core, parent)

	def set(self, range_mode: enums.TriggerWinRangeMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:WINDow:RANGe \n
		Snippet: driver.trigger.event.window.range.set(range_mode = enums.TriggerWinRangeMode.ENTer, evnt = repcap.Evnt.Default) \n
		Selects how the signal run is compared with the window. \n
			:param range_mode:
				- ENTer: Triggers when the signal crosses the upper or lower level and thus enters the window made up of these two levels.
				- EXIT: Triggers when the signal leaves the window.
				- WITHin: Triggers if the signal stays between the upper and lower level for a specified time. The time is defined with TRIGger:EVENtev:WINDow:TIME.
				- OUTSide: Triggers if the signal stays above the upper level or below the lower level for a specified time. The time is defined with TRIGger:EVENtev:WINDow:TIME.
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')"""
		param = Conversions.enum_scalar_to_str(range_mode, enums.TriggerWinRangeMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:WINDow:RANGe {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.TriggerWinRangeMode:
		"""TRIGger:EVENt<*>:WINDow:RANGe \n
		Snippet: value: enums.TriggerWinRangeMode = driver.trigger.event.window.range.get(evnt = repcap.Evnt.Default) \n
		Selects how the signal run is compared with the window. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: range_mode:
				- ENTer: Triggers when the signal crosses the upper or lower level and thus enters the window made up of these two levels.
				- EXIT: Triggers when the signal leaves the window.
				- WITHin: Triggers if the signal stays between the upper and lower level for a specified time. The time is defined with TRIGger:EVENtev:WINDow:TIME.
				- OUTSide: Triggers if the signal stays above the upper level or below the lower level for a specified time. The time is defined with TRIGger:EVENtev:WINDow:TIME."""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:WINDow:RANGe?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerWinRangeMode)
