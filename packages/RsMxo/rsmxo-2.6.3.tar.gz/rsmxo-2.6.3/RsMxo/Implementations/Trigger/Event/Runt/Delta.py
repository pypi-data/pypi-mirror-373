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

	def set(self, width_delta: float, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:RUNT:DELTa \n
		Snippet: driver.trigger.event.runt.delta.set(width_delta = 1.0, evnt = repcap.Evnt.Default) \n
		Defines a range around the runt width specified using method RsMxo.Trigger.Event.Runt.Width.set. Available if method
		RsMxo.Trigger.Event.Runt.Range.set is set to WITHin or OUTSide. \n
			:param width_delta: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(width_delta)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:RUNT:DELTa {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:RUNT:DELTa \n
		Snippet: value: float = driver.trigger.event.runt.delta.get(evnt = repcap.Evnt.Default) \n
		Defines a range around the runt width specified using method RsMxo.Trigger.Event.Runt.Width.set. Available if method
		RsMxo.Trigger.Event.Runt.Range.set is set to WITHin or OUTSide. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: width_delta: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:RUNT:DELTa?')
		return Conversions.str_to_float(response)
