from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, first: bool, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:ENABle \n
		Snippet: driver.gate.enable.set(first = False, gate = repcap.Gate.Default) \n
		Enables the gate. \n
			:param first: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = Conversions.bool_to_str(first)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:ENABle {param}')

	def get(self, gate=repcap.Gate.Default) -> bool:
		"""GATE<*>:ENABle \n
		Snippet: value: bool = driver.gate.enable.get(gate = repcap.Gate.Default) \n
		Enables the gate. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: first: No help available"""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
