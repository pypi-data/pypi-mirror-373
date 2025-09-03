from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class X1PositionCls:
	"""X1Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("x1Position", core, parent)

	def set(self, x_1_position: float, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:X1Position \n
		Snippet: driver.cursor.x1Position.set(x_1_position = 1.0, cursor = repcap.Cursor.Default) \n
		Defines the position of the left vertical cursor line. \n
			:param x_1_position: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.decimal_value_to_str(x_1_position)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:X1Position {param}')

	def get(self, cursor=repcap.Cursor.Default) -> float:
		"""CURSor<*>:X1Position \n
		Snippet: value: float = driver.cursor.x1Position.get(cursor = repcap.Cursor.Default) \n
		Defines the position of the left vertical cursor line. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: x_1_position: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:X1Position?')
		return Conversions.str_to_float(response)
