from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def set(self, events: int, sequence=repcap.Sequence.Default) -> None:
		"""TRIGger:MEVents:SEQuence<*>:COUNt \n
		Snippet: driver.trigger.mevents.sequence.count.set(events = 1, sequence = repcap.Sequence.Default) \n
		Sets the number of B-trigger conditions to be fulfilled after an A-trigger. The last B-trigger causes the trigger event.
		The waiting time for B-triggers can be restricted with a reset condition: timeout or reset event. \n
			:param events: No help available
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
		"""
		param = Conversions.decimal_value_to_str(events)
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		self._core.io.write(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:COUNt {param}')

	def get(self, sequence=repcap.Sequence.Default) -> int:
		"""TRIGger:MEVents:SEQuence<*>:COUNt \n
		Snippet: value: int = driver.trigger.mevents.sequence.count.get(sequence = repcap.Sequence.Default) \n
		Sets the number of B-trigger conditions to be fulfilled after an A-trigger. The last B-trigger causes the trigger event.
		The waiting time for B-triggers can be restricted with a reset condition: timeout or reset event. \n
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
			:return: events: No help available"""
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		response = self._core.io.query_str(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
