from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DelayCls:
	"""Delay commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("delay", core, parent)

	def set(self, delay: float, sequence=repcap.Sequence.Default) -> None:
		"""TRIGger:MEVents:SEQuence<*>:DELay \n
		Snippet: driver.trigger.mevents.sequence.delay.set(delay = 1.0, sequence = repcap.Sequence.Default) \n
		Sets the time that the instrument waits after an A-trigger until it recognizes B-triggers. \n
			:param delay: No help available
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
		"""
		param = Conversions.decimal_value_to_str(delay)
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		self._core.io.write(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:DELay {param}')

	def get(self, sequence=repcap.Sequence.Default) -> float:
		"""TRIGger:MEVents:SEQuence<*>:DELay \n
		Snippet: value: float = driver.trigger.mevents.sequence.delay.get(sequence = repcap.Sequence.Default) \n
		Sets the time that the instrument waits after an A-trigger until it recognizes B-triggers. \n
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
			:return: delay: No help available"""
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		response = self._core.io.query_str(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:DELay?')
		return Conversions.str_to_float(response)
