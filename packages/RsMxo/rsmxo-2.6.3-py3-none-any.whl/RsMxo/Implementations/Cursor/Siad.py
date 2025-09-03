from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SiadCls:
	"""Siad commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("siad", core, parent)

	def set(self, shw_in_all_diags: bool, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:SIAD \n
		Snippet: driver.cursor.siad.set(shw_in_all_diags = False, cursor = repcap.Cursor.Default) \n
		Shows the enabled cursor measurements in all active diagrams of the time domain. In the spectrum domain, the setting is
		disabled. The cursors are shown only on the source spectrum of the measurement. \n
			:param shw_in_all_diags: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.bool_to_str(shw_in_all_diags)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:SIAD {param}')

	def get(self, cursor=repcap.Cursor.Default) -> bool:
		"""CURSor<*>:SIAD \n
		Snippet: value: bool = driver.cursor.siad.get(cursor = repcap.Cursor.Default) \n
		Shows the enabled cursor measurements in all active diagrams of the time domain. In the spectrum domain, the setting is
		disabled. The cursors are shown only on the source spectrum of the measurement. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: shw_in_all_diags: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:SIAD?')
		return Conversions.str_to_bool(response)
