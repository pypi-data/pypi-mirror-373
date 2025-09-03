from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FunctionCls:
	"""Function commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("function", core, parent)

	def set(self, type_py: enums.CursorType, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:FUNCtion \n
		Snippet: driver.cursor.function.set(type_py = enums.CursorType.HORizontal, cursor = repcap.Cursor.Default) \n
		Defines the cursor type to be used for the measurement. \n
			:param type_py:
				- HORizontal: A pair of horizontal cursor lines.
				- VERTical: A pair of vertical cursor lines.
				- PAIRed: Both vertical and horizontal cursor line pairs.
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')"""
		param = Conversions.enum_scalar_to_str(type_py, enums.CursorType)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:FUNCtion {param}')

	# noinspection PyTypeChecker
	def get(self, cursor=repcap.Cursor.Default) -> enums.CursorType:
		"""CURSor<*>:FUNCtion \n
		Snippet: value: enums.CursorType = driver.cursor.function.get(cursor = repcap.Cursor.Default) \n
		Defines the cursor type to be used for the measurement. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: type_py:
				- HORizontal: A pair of horizontal cursor lines.
				- VERTical: A pair of vertical cursor lines.
				- PAIRed: Both vertical and horizontal cursor line pairs."""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:FUNCtion?')
		return Conversions.str_to_scalar_enum(response, enums.CursorType)
