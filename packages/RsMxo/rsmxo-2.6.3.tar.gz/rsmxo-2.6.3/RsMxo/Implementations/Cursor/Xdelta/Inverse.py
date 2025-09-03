from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class InverseCls:
	"""Inverse commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("inverse", core, parent)

	def get(self, cursor=repcap.Cursor.Default) -> float:
		"""CURSor<*>:XDELta:INVerse \n
		Snippet: value: float = driver.cursor.xdelta.inverse.get(cursor = repcap.Cursor.Default) \n
		Queries the inverse value of the delta value (distance) of the two vertical cursor lines. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: delta_inverse: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:XDELta:INVerse?')
		return Conversions.str_to_float(response)
