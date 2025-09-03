from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:STATe \n
		Snippet: driver.cursor.state.set(state = False, cursor = repcap.Cursor.Default) \n
		Enables the selected cursor measurement. \n
			:param state: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.bool_to_str(state)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:STATe {param}')

	def get(self, cursor=repcap.Cursor.Default) -> bool:
		"""CURSor<*>:STATe \n
		Snippet: value: bool = driver.cursor.state.get(cursor = repcap.Cursor.Default) \n
		Enables the selected cursor measurement. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: state: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
