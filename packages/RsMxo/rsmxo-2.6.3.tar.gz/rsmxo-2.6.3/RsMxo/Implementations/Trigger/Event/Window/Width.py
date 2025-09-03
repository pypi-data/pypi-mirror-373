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
		"""TRIGger:EVENt<*>:WINDow:WIDTh \n
		Snippet: driver.trigger.event.window.width.set(width = 1.0, evnt = repcap.Evnt.Default) \n
		Depending on the values of method RsMxo.Trigger.Event.Window.Range.set the width sets:
			INTRO_CMD_HELP: To define the path and file names, use the EXPort:WAVeform:AUTonaming:* commands: \n
			- For the ranges Within and Outside, the width defines the center of a time range. The range is defined by the limits ±Delta, see method RsMxo.Trigger.Event.Window.Delta.set.
			- For the ranges Shorter and Longer, it defines the maximum and minimum time lapse, respectively.  \n
			:param width: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(width)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:WINDow:WIDTh {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:WINDow:WIDTh \n
		Snippet: value: float = driver.trigger.event.window.width.get(evnt = repcap.Evnt.Default) \n
		Depending on the values of method RsMxo.Trigger.Event.Window.Range.set the width sets:
			INTRO_CMD_HELP: To define the path and file names, use the EXPort:WAVeform:AUTonaming:* commands: \n
			- For the ranges Within and Outside, the width defines the center of a time range. The range is defined by the limits ±Delta, see method RsMxo.Trigger.Event.Window.Delta.set.
			- For the ranges Shorter and Longer, it defines the maximum and minimum time lapse, respectively.  \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: width: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:WINDow:WIDTh?')
		return Conversions.str_to_float(response)
