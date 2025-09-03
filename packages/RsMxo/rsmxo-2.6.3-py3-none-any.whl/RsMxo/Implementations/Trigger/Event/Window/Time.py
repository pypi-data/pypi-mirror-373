from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimeCls:
	"""Time commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def set(self, time_range_mode: enums.RangeMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:WINDow:TIME \n
		Snippet: driver.trigger.event.window.time.set(time_range_mode = enums.RangeMode.LONGer, evnt = repcap.Evnt.Default) \n
		Available for method RsMxo.Trigger.Event.Window.Range.set = WITHin and OUTSide. Selects how the time limit of the window
		is defined. You can specify the width with method RsMxo.Trigger.Event.Window.Width.set and the delta with method RsMxo.
		Trigger.Event.Window.Delta.set. \n
			:param time_range_mode:
				- WITHin: Triggers if the signal stays inside or outside the vertical window limits at least for the time Width - Delta and for Width + Delta at the most.
				- OUTSide: Outside is the opposite definition of Within. The instrument triggers if the signal stays inside or outside the vertical window limits for a time shorter than Width - Delta or longer than Width + Delta.
				- SHORter: Triggers if the signal crosses vertical limits before the specified width time is reached.
				- LONGer: Triggers if the signal crosses vertical limits before the specified width time is reached.
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')"""
		param = Conversions.enum_scalar_to_str(time_range_mode, enums.RangeMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:WINDow:TIME {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.RangeMode:
		"""TRIGger:EVENt<*>:WINDow:TIME \n
		Snippet: value: enums.RangeMode = driver.trigger.event.window.time.get(evnt = repcap.Evnt.Default) \n
		Available for method RsMxo.Trigger.Event.Window.Range.set = WITHin and OUTSide. Selects how the time limit of the window
		is defined. You can specify the width with method RsMxo.Trigger.Event.Window.Width.set and the delta with method RsMxo.
		Trigger.Event.Window.Delta.set. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: time_range_mode:
				- WITHin: Triggers if the signal stays inside or outside the vertical window limits at least for the time Width - Delta and for Width + Delta at the most.
				- OUTSide: Outside is the opposite definition of Within. The instrument triggers if the signal stays inside or outside the vertical window limits for a time shorter than Width - Delta or longer than Width + Delta.
				- SHORter: Triggers if the signal crosses vertical limits before the specified width time is reached.
				- LONGer: Triggers if the signal crosses vertical limits before the specified width time is reached."""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:WINDow:TIME?')
		return Conversions.str_to_scalar_enum(response, enums.RangeMode)
