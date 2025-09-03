from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NextCls:
	"""Next commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("next", core, parent)

	def set(self, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:MAXimum:NEXT \n
		Snippet: driver.cursor.maximum.next.set(cursor = repcap.Cursor.Default) \n
		Cursor 2 is set to the next smaller absolute peak from the current position. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:MAXimum:NEXT')

	def set_and_wait(self, cursor=repcap.Cursor.Default, opc_timeout_ms: int = -1) -> None:
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		"""CURSor<*>:MAXimum:NEXT \n
		Snippet: driver.cursor.maximum.next.set_and_wait(cursor = repcap.Cursor.Default) \n
		Cursor 2 is set to the next smaller absolute peak from the current position. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CURSor{cursor_cmd_val}:MAXimum:NEXT', opc_timeout_ms)
