from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RateCls:
	"""Rate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rate", core, parent)

	def set(self, time: float, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SLEW:RATE \n
		Snippet: driver.trigger.event.slew.rate.set(time = 1.0, evnt = repcap.Evnt.Default) \n
		For method RsMxo.Trigger.Event.Slew.Range.set = INSRange and OUTRange, the slew rate defines the center of a range which
		is defined by the limits ±Delta. For method RsMxo.Trigger.Event.Slew.Range.set = LTHan and GTHan, the slew rate defines
		the maximum and minimum slew rate limits, respectively. When the signal crosses this level, the slew rate measurement
		starts or stops depending on the selected slope (see method RsMxo.Trigger.Event.Slew.Slope.set) . \n
			:param time: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(time)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SLEW:RATE {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:SLEW:RATE \n
		Snippet: value: float = driver.trigger.event.slew.rate.get(evnt = repcap.Evnt.Default) \n
		For method RsMxo.Trigger.Event.Slew.Range.set = INSRange and OUTRange, the slew rate defines the center of a range which
		is defined by the limits ±Delta. For method RsMxo.Trigger.Event.Slew.Range.set = LTHan and GTHan, the slew rate defines
		the maximum and minimum slew rate limits, respectively. When the signal crosses this level, the slew rate measurement
		starts or stops depending on the selected slope (see method RsMxo.Trigger.Event.Slew.Slope.set) . \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: time: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SLEW:RATE?')
		return Conversions.str_to_float(response)
