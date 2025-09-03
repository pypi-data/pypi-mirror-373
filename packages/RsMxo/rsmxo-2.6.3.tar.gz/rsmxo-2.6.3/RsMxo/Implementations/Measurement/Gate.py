from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GateCls:
	"""Gate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gate", core, parent)

	def set(self, gate: int, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:GATE \n
		Snippet: driver.measurement.gate.set(gate = 1, measIndex = repcap.MeasIndex.Default) \n
		Sets the gate of the indicated measurement. Enable a gate before you assign a measurement to it (method RsMxo.Gate.Enable.
		set =ON) . The query returns 0, if no gate is assigned. \n
			:param gate: Number of the gate to be used
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(gate)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:GATE {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> int:
		"""MEASurement<*>:GATE \n
		Snippet: value: int = driver.measurement.gate.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the gate of the indicated measurement. Enable a gate before you assign a measurement to it (method RsMxo.Gate.Enable.
		set =ON) . The query returns 0, if no gate is assigned. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: gate: Number of the gate to be used"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:GATE?')
		return Conversions.str_to_int(response)
