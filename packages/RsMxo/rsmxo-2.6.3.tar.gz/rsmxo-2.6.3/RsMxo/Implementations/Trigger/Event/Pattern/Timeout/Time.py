from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimeCls:
	"""Time commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def set(self, time: float, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:TIMeout[:TIME] \n
		Snippet: driver.trigger.event.pattern.timeout.time.set(time = 1.0, evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param time: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(time)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:TIMeout:TIME {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:PATTern:TIMeout[:TIME] \n
		Snippet: value: float = driver.trigger.event.pattern.timeout.time.get(evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: time: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:TIMeout:TIME?')
		return Conversions.str_to_float(response)
