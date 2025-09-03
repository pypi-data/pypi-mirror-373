from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get(self, cursor=repcap.Cursor.Default) -> int:
		"""CURSor<*>:COUNt \n
		Snippet: value: int = driver.cursor.count.get(cursor = repcap.Cursor.Default) \n
		Returns the maximum number of cursor sets, which is the maximum value for the cursor suffix. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: count: Number of cursor sets"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
