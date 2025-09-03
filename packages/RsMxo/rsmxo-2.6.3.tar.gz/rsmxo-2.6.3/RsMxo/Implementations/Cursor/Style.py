from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StyleCls:
	"""Style commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("style", core, parent)

	def set(self, style: enums.CursorStyle, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:STYLe \n
		Snippet: driver.cursor.style.set(style = enums.CursorStyle.LINes, cursor = repcap.Cursor.Default) \n
		Defines how the cursor is displayed in the diagram. \n
			:param style:
				- LINes: The cursors are displayed as lines.
				- LRHombus: The cursors are displayed as lines. The intersections of the cursors with the waveforms are displayed by rhombus-shaped points.
				- VLRHombus: The cursors are displayed only as vertical lines. The intersections of the cursors with the waveforms are displayed by rhombus-shaped points.
				- RHOMbus: The intersections of the cursors with the waveforms are displayed by rhombus-shaped points.
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')"""
		param = Conversions.enum_scalar_to_str(style, enums.CursorStyle)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:STYLe {param}')

	# noinspection PyTypeChecker
	def get(self, cursor=repcap.Cursor.Default) -> enums.CursorStyle:
		"""CURSor<*>:STYLe \n
		Snippet: value: enums.CursorStyle = driver.cursor.style.get(cursor = repcap.Cursor.Default) \n
		Defines how the cursor is displayed in the diagram. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: style:
				- LINes: The cursors are displayed as lines.
				- LRHombus: The cursors are displayed as lines. The intersections of the cursors with the waveforms are displayed by rhombus-shaped points.
				- VLRHombus: The cursors are displayed only as vertical lines. The intersections of the cursors with the waveforms are displayed by rhombus-shaped points.
				- RHOMbus: The intersections of the cursors with the waveforms are displayed by rhombus-shaped points."""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:STYLe?')
		return Conversions.str_to_scalar_enum(response, enums.CursorStyle)
