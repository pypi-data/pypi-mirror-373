from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def set(self, show_label: bool, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:LABel \n
		Snippet: driver.cursor.label.set(show_label = False, cursor = repcap.Cursor.Default) \n
		Shows the cursor labels in the diagram. \n
			:param show_label: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.bool_to_str(show_label)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:LABel {param}')

	def get(self, cursor=repcap.Cursor.Default) -> bool:
		"""CURSor<*>:LABel \n
		Snippet: value: bool = driver.cursor.label.get(cursor = repcap.Cursor.Default) \n
		Shows the cursor labels in the diagram. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: show_label: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:LABel?')
		return Conversions.str_to_bool(response)
