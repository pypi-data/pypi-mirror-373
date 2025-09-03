from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StopCls:
	"""Stop commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stop", core, parent)

	def set(self, relative_stop: float, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:RELative:STOP \n
		Snippet: driver.gate.relative.stop.set(relative_stop = 1.0, gate = repcap.Gate.Default) \n
		Define the relative start and end values for the gate, respectively. Available, if method RsMxo.Gate.Gcoupling.
		set = MANUal and method RsMxo.Gate.Mode.set =REL. \n
			:param relative_stop: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = Conversions.decimal_value_to_str(relative_stop)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:RELative:STOP {param}')

	def get(self, gate=repcap.Gate.Default) -> float:
		"""GATE<*>:RELative:STOP \n
		Snippet: value: float = driver.gate.relative.stop.get(gate = repcap.Gate.Default) \n
		Define the relative start and end values for the gate, respectively. Available, if method RsMxo.Gate.Gcoupling.
		set = MANUal and method RsMxo.Gate.Mode.set =REL. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: relative_stop: No help available"""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:RELative:STOP?')
		return Conversions.str_to_float(response)
