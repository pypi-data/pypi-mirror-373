from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, state: bool, sequence=repcap.Sequence.Default) -> None:
		"""TRIGger:MEVents:SEQuence<*>:RESet:TIMeout[:ENABle] \n
		Snippet: driver.trigger.mevents.sequence.reset.timeout.enable.set(state = False, sequence = repcap.Sequence.Default) \n
		If set to ON, the instrument waits for the time defined using method RsMxo.Trigger.Mevents.Sequence.Reset.Timeout.Time.
		set for the specified number of B-events. If no trigger occurs during that time, the sequence is restarted with the
		A-event. \n
			:param state: No help available
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
		"""
		param = Conversions.bool_to_str(state)
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		self._core.io.write(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:RESet:TIMeout:ENABle {param}')

	def get(self, sequence=repcap.Sequence.Default) -> bool:
		"""TRIGger:MEVents:SEQuence<*>:RESet:TIMeout[:ENABle] \n
		Snippet: value: bool = driver.trigger.mevents.sequence.reset.timeout.enable.get(sequence = repcap.Sequence.Default) \n
		If set to ON, the instrument waits for the time defined using method RsMxo.Trigger.Mevents.Sequence.Reset.Timeout.Time.
		set for the specified number of B-events. If no trigger occurs during that time, the sequence is restarted with the
		A-event. \n
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
			:return: state: No help available"""
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		response = self._core.io.query_str(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:RESet:TIMeout:ENABle?')
		return Conversions.str_to_bool(response)
