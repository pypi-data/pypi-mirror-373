from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def set(self, label: str, cursor=repcap.Cursor.Default, horizontal=repcap.Horizontal.Default) -> None:
		"""CURSor<*>:HORizontal<*>:LABel \n
		Snippet: driver.cursor.horizontal.label.set(label = 'abc', cursor = repcap.Cursor.Default, horizontal = repcap.Horizontal.Default) \n
		Defines the label to be displayed with the horizontal cursor lines. By default, the cursors are labeled as Cu1.1, Cu1.2,
		Cu2.1, ... \n
			:param label: String with the cursor label
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:param horizontal: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Horizontal')
		"""
		param = Conversions.value_to_quoted_str(label)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		horizontal_cmd_val = self._cmd_group.get_repcap_cmd_value(horizontal, repcap.Horizontal)
		self._core.io.write(f'CURSor{cursor_cmd_val}:HORizontal{horizontal_cmd_val}:LABel {param}')

	def get(self, cursor=repcap.Cursor.Default, horizontal=repcap.Horizontal.Default) -> str:
		"""CURSor<*>:HORizontal<*>:LABel \n
		Snippet: value: str = driver.cursor.horizontal.label.get(cursor = repcap.Cursor.Default, horizontal = repcap.Horizontal.Default) \n
		Defines the label to be displayed with the horizontal cursor lines. By default, the cursors are labeled as Cu1.1, Cu1.2,
		Cu2.1, ... \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:param horizontal: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Horizontal')
			:return: label: String with the cursor label"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		horizontal_cmd_val = self._cmd_group.get_repcap_cmd_value(horizontal, repcap.Horizontal)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:HORizontal{horizontal_cmd_val}:LABel?')
		return trim_str_response(response)
