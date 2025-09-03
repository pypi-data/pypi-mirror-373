from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ShowCls:
	"""Show commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("show", core, parent)

	def set(self, display_state: bool, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:SHOW \n
		Snippet: driver.gate.show.set(display_state = False, gate = repcap.Gate.Default) \n
		If enabled, the gate area is indicated in the source diagram. \n
			:param display_state: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = Conversions.bool_to_str(display_state)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:SHOW {param}')

	def get(self, gate=repcap.Gate.Default) -> bool:
		"""GATE<*>:SHOW \n
		Snippet: value: bool = driver.gate.show.get(gate = repcap.Gate.Default) \n
		If enabled, the gate area is indicated in the source diagram. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: display_state: No help available"""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:SHOW?')
		return Conversions.str_to_bool(response)
