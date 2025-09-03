from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WidthCls:
	"""Width commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("width", core, parent)

	def set(self, width: float, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:INTerval:WIDTh \n
		Snippet: driver.trigger.event.interval.width.set(width = 1.0, evnt = repcap.Evnt.Default) \n
		Sets the time between two pulses for the interval trigger. \n
			:param width: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(width)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:INTerval:WIDTh {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:INTerval:WIDTh \n
		Snippet: value: float = driver.trigger.event.interval.width.get(evnt = repcap.Evnt.Default) \n
		Sets the time between two pulses for the interval trigger. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: width: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:INTerval:WIDTh?')
		return Conversions.str_to_float(response)
