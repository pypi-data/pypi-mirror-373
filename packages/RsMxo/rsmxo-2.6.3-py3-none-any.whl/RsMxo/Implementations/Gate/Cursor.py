from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CursorCls:
	"""Cursor commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cursor", core, parent)

	def set(self, cursor: enums.Cursor, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:CURSor \n
		Snippet: driver.gate.cursor.set(cursor = enums.Cursor.CURSOR1, gate = repcap.Gate.Default) \n
		Available for method RsMxo.Gate.Gcoupling.set = CURSor. Selects the cursor set to be used for measurement gating.
		The gate area is defined by the cursor lines. \n
			:param cursor: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = Conversions.enum_scalar_to_str(cursor, enums.Cursor)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:CURSor {param}')

	# noinspection PyTypeChecker
	def get(self, gate=repcap.Gate.Default) -> enums.Cursor:
		"""GATE<*>:CURSor \n
		Snippet: value: enums.Cursor = driver.gate.cursor.get(gate = repcap.Gate.Default) \n
		Available for method RsMxo.Gate.Gcoupling.set = CURSor. Selects the cursor set to be used for measurement gating.
		The gate area is defined by the cursor lines. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: cursor: No help available"""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:CURSor?')
		return Conversions.str_to_scalar_enum(response, enums.Cursor)
