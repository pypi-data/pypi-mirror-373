from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class YcouplingCls:
	"""Ycoupling commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ycoupling", core, parent)

	def set(self, coupling: bool, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:YCOupling \n
		Snippet: driver.cursor.ycoupling.set(coupling = False, cursor = repcap.Cursor.Default) \n
		Defines the positioning mode of the horizontal cursor. If the horizontal cursor lines track the waveform, the y coupling
		is irrelevant (method RsMxo.Cursor.Tracking.State.set is ON) . \n
			:param coupling:
				- ON: Moving one cursor line moves the other cursor line too. The cursor lines always remain a fixed distance.
				- OFF: Each cursor line is positioned independently.
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')"""
		param = Conversions.bool_to_str(coupling)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:YCOupling {param}')

	def get(self, cursor=repcap.Cursor.Default) -> bool:
		"""CURSor<*>:YCOupling \n
		Snippet: value: bool = driver.cursor.ycoupling.get(cursor = repcap.Cursor.Default) \n
		Defines the positioning mode of the horizontal cursor. If the horizontal cursor lines track the waveform, the y coupling
		is irrelevant (method RsMxo.Cursor.Tracking.State.set is ON) . \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: coupling:
				- ON: Moving one cursor line moves the other cursor line too. The cursor lines always remain a fixed distance.
				- OFF: Each cursor line is positioned independently."""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:YCOupling?')
		return Conversions.str_to_bool(response)
