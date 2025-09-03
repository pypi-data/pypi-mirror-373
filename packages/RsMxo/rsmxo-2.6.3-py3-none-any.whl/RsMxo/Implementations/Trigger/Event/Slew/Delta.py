from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DeltaCls:
	"""Delta commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("delta", core, parent)

	def set(self, time_delta: float, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SLEW:DELTa \n
		Snippet: driver.trigger.event.slew.delta.set(time_delta = 1.0, evnt = repcap.Evnt.Default) \n
		Defines a time range around the given slew rate. \n
			:param time_delta: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(time_delta)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SLEW:DELTa {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:SLEW:DELTa \n
		Snippet: value: float = driver.trigger.event.slew.delta.get(evnt = repcap.Evnt.Default) \n
		Defines a time range around the given slew rate. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: time_delta: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SLEW:DELTa?')
		return Conversions.str_to_float(response)
