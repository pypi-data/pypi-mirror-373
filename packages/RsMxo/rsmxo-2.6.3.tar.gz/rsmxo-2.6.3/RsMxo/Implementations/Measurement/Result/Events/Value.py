from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def get(self, measIndex=repcap.MeasIndex.Default) -> float:
		"""MEASurement<*>:RESult:EVENts:VALue \n
		Snippet: value: float = driver.measurement.result.events.value.get(measIndex = repcap.MeasIndex.Default) \n
		Returns the measured value of the indicated measured event. The command is relevant for measurements of all events, see
		method RsMxo.Measurement.Multiple.set. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: event_value: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:RESult:EVENts:VALue?')
		return Conversions.str_to_float(response)
