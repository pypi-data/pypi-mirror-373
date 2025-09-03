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

	def set(self, range_mode: enums.TriggerSlewRangeMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SLEW:RANGe \n
		Snippet: driver.trigger.event.slew.range.set(range_mode = enums.TriggerSlewRangeMode.GTHan, evnt = repcap.Evnt.Default) \n
		Selects how the time limit for the slew rate is defined. The time measurement starts when the signal crosses the first
		trigger level - the upper or lower limit depending on the selected slope. The measurement stops when the signal crosses
		the second level. You can select the rate with method RsMxo.Trigger.Event.Slew.Rate.set and set the delta with method
		RsMxo.Trigger.Event.Slew.Delta.set. \n
			:param range_mode:
				- INSRange: Triggers on pulses inside a given range. The range is defined by the slew rate ±delta.
				- OUTRange: Triggers on pulses outside a given range. The range is defined by the slew rate ±delta.
				- LTHan: Triggers on pulses shorter than the given slew rate.
				- GTHan: Triggers on pulses longer than the given slew rate.
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')"""
		param = Conversions.enum_scalar_to_str(range_mode, enums.TriggerSlewRangeMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SLEW:RANGe {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.TriggerSlewRangeMode:
		"""TRIGger:EVENt<*>:SLEW:RANGe \n
		Snippet: value: enums.TriggerSlewRangeMode = driver.trigger.event.slew.range.get(evnt = repcap.Evnt.Default) \n
		Selects how the time limit for the slew rate is defined. The time measurement starts when the signal crosses the first
		trigger level - the upper or lower limit depending on the selected slope. The measurement stops when the signal crosses
		the second level. You can select the rate with method RsMxo.Trigger.Event.Slew.Rate.set and set the delta with method
		RsMxo.Trigger.Event.Slew.Delta.set. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: range_mode:
				- INSRange: Triggers on pulses inside a given range. The range is defined by the slew rate ±delta.
				- OUTRange: Triggers on pulses outside a given range. The range is defined by the slew rate ±delta.
				- LTHan: Triggers on pulses shorter than the given slew rate.
				- GTHan: Triggers on pulses longer than the given slew rate."""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SLEW:RANGe?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerSlewRangeMode)
