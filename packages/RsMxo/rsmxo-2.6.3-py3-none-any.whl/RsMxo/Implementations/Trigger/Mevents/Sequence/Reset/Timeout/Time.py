from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimeCls:
	"""Time commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def set(self, reset_timeout: float, sequence=repcap.Sequence.Default) -> None:
		"""TRIGger:MEVents:SEQuence<*>:RESet:TIMeout:TIME \n
		Snippet: driver.trigger.mevents.sequence.reset.timeout.time.set(reset_timeout = 1.0, sequence = repcap.Sequence.Default) \n
		The time the instrument waits for the number of B-events specified using method RsMxo.Trigger.Mevents.Sequence.Count.set,
		before the sequence is restarted with the A-trigger. \n
			:param reset_timeout: No help available
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
		"""
		param = Conversions.decimal_value_to_str(reset_timeout)
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		self._core.io.write(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:RESet:TIMeout:TIME {param}')

	def get(self, sequence=repcap.Sequence.Default) -> float:
		"""TRIGger:MEVents:SEQuence<*>:RESet:TIMeout:TIME \n
		Snippet: value: float = driver.trigger.mevents.sequence.reset.timeout.time.get(sequence = repcap.Sequence.Default) \n
		The time the instrument waits for the number of B-events specified using method RsMxo.Trigger.Mevents.Sequence.Count.set,
		before the sequence is restarted with the A-trigger. \n
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
			:return: reset_timeout: No help available"""
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		response = self._core.io.query_str(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:RESet:TIMeout:TIME?')
		return Conversions.str_to_float(response)
