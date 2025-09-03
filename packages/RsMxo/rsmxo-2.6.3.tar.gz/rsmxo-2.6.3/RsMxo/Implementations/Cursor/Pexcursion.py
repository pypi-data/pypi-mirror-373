from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PexcursionCls:
	"""Pexcursion commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pexcursion", core, parent)

	def set(self, value: float, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:PEXCursion \n
		Snippet: driver.cursor.pexcursion.set(value = 1.0, cursor = repcap.Cursor.Default) \n
		Sets the minimum level by which the waveform must rise or fall so that it will be identified as a maximum or a minimum by
		the search functions. \n
			:param value: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.decimal_value_to_str(value)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:PEXCursion {param}')

	def get(self, cursor=repcap.Cursor.Default) -> float:
		"""CURSor<*>:PEXCursion \n
		Snippet: value: float = driver.cursor.pexcursion.get(cursor = repcap.Cursor.Default) \n
		Sets the minimum level by which the waveform must rise or fall so that it will be identified as a maximum or a minimum by
		the search functions. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: value: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:PEXCursion?')
		return Conversions.str_to_float(response)
