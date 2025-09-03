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

	def set(self, stop: float, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:ABSolute:STOP \n
		Snippet: driver.gate.absolute.stop.set(stop = 1.0, gate = repcap.Gate.Default) \n
		Define the absolute start and end values for the gate, respectively. Available, if method RsMxo.Gate.Gcoupling.
		set = MANUal and method RsMxo.Gate.Mode.set =ABS. \n
			:param stop: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = Conversions.decimal_value_to_str(stop)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:ABSolute:STOP {param}')

	def get(self, gate=repcap.Gate.Default) -> float:
		"""GATE<*>:ABSolute:STOP \n
		Snippet: value: float = driver.gate.absolute.stop.get(gate = repcap.Gate.Default) \n
		Define the absolute start and end values for the gate, respectively. Available, if method RsMxo.Gate.Gcoupling.
		set = MANUal and method RsMxo.Gate.Mode.set =ABS. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: stop: No help available"""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:ABSolute:STOP?')
		return Conversions.str_to_float(response)
