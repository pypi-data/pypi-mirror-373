from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, mode: enums.AbsRel, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:MODE \n
		Snippet: driver.gate.mode.set(mode = enums.AbsRel.ABS, gate = repcap.Gate.Default) \n
		Selects if the gate settings are configured using absolute or relative values. \n
			:param mode: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.AbsRel)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, gate=repcap.Gate.Default) -> enums.AbsRel:
		"""GATE<*>:MODE \n
		Snippet: value: enums.AbsRel = driver.gate.mode.get(gate = repcap.Gate.Default) \n
		Selects if the gate settings are configured using absolute or relative values. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: mode: No help available"""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AbsRel)
