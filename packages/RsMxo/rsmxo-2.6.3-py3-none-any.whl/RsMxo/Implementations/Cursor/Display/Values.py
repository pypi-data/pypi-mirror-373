from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValuesCls:
	"""Values commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("values", core, parent)

	def set(self, add_values_label: bool, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:DISPlay:VALues \n
		Snippet: driver.cursor.display.values.set(add_values_label = False, cursor = repcap.Cursor.Default) \n
		Shows the measured values in the cursor labels. \n
			:param add_values_label: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.bool_to_str(add_values_label)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:DISPlay:VALues {param}')

	def get(self, cursor=repcap.Cursor.Default) -> bool:
		"""CURSor<*>:DISPlay:VALues \n
		Snippet: value: bool = driver.cursor.display.values.get(cursor = repcap.Cursor.Default) \n
		Shows the measured values in the cursor labels. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: add_values_label: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:DISPlay:VALues?')
		return Conversions.str_to_bool(response)
