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

	def set(self, range_mode: enums.RangeMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:INTerval:RANGe \n
		Snippet: driver.trigger.event.interval.range.set(range_mode = enums.RangeMode.LONGer, evnt = repcap.Evnt.Default) \n
		Defines the range of an interval in relation to the interval width specified using method RsMxo.Trigger.Event.Interval.
		Width.set and method RsMxo.Trigger.Event.Interval.Delta.set. \n
			:param range_mode:
				- WITHin: Triggers on pulses inside a given range. The range is defined by the interval width ±delta.
				- OUTSide: Triggers on pulses outside a given range. The range is defined by the interval width ±delta.
				- SHORter: Triggers on pulses shorter than the given interval width.
				- LONGer: Triggers on pulses longer than the given interval width.
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')"""
		param = Conversions.enum_scalar_to_str(range_mode, enums.RangeMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:INTerval:RANGe {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.RangeMode:
		"""TRIGger:EVENt<*>:INTerval:RANGe \n
		Snippet: value: enums.RangeMode = driver.trigger.event.interval.range.get(evnt = repcap.Evnt.Default) \n
		Defines the range of an interval in relation to the interval width specified using method RsMxo.Trigger.Event.Interval.
		Width.set and method RsMxo.Trigger.Event.Interval.Delta.set. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: range_mode:
				- WITHin: Triggers on pulses inside a given range. The range is defined by the interval width ±delta.
				- OUTSide: Triggers on pulses outside a given range. The range is defined by the interval width ±delta.
				- SHORter: Triggers on pulses shorter than the given interval width.
				- LONGer: Triggers on pulses longer than the given interval width."""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:INTerval:RANGe?')
		return Conversions.str_to_scalar_enum(response, enums.RangeMode)
