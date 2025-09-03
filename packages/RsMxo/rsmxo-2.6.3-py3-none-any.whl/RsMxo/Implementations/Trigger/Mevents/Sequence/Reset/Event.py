from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EventCls:
	"""Event commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("event", core, parent)

	def set(self, enab_rst_evt: bool, sequence=repcap.Sequence.Default) -> None:
		"""TRIGger:MEVents:SEQuence<*>:RESet:EVENt \n
		Snippet: driver.trigger.mevents.sequence.reset.event.set(enab_rst_evt = False, sequence = repcap.Sequence.Default) \n
		If enabled, the trigger sequence is restarted by the R-trigger condition if the specified number of B-triggers does not
		occur before the R-trigger conditions are fulfilled. \n
			:param enab_rst_evt: No help available
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
		"""
		param = Conversions.bool_to_str(enab_rst_evt)
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		self._core.io.write(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:RESet:EVENt {param}')

	def get(self, sequence=repcap.Sequence.Default) -> bool:
		"""TRIGger:MEVents:SEQuence<*>:RESet:EVENt \n
		Snippet: value: bool = driver.trigger.mevents.sequence.reset.event.get(sequence = repcap.Sequence.Default) \n
		If enabled, the trigger sequence is restarted by the R-trigger condition if the specified number of B-triggers does not
		occur before the R-trigger conditions are fulfilled. \n
			:param sequence: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sequence')
			:return: enab_rst_evt: No help available"""
		sequence_cmd_val = self._cmd_group.get_repcap_cmd_value(sequence, repcap.Sequence)
		response = self._core.io.query_str(f'TRIGger:MEVents:SEQuence{sequence_cmd_val}:RESet:EVENt?')
		return Conversions.str_to_bool(response)
