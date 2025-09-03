from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, track_curve: bool, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:TRACking[:STATe] \n
		Snippet: driver.cursor.tracking.state.set(track_curve = False, cursor = repcap.Cursor.Default) \n
		If enabled, the horizontal cursor lines follow the waveform. \n
			:param track_curve: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.bool_to_str(track_curve)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:TRACking:STATe {param}')

	def get(self, cursor=repcap.Cursor.Default) -> bool:
		"""CURSor<*>:TRACking[:STATe] \n
		Snippet: value: bool = driver.cursor.tracking.state.get(cursor = repcap.Cursor.Default) \n
		If enabled, the horizontal cursor lines follow the waveform. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: track_curve: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:TRACking:STATe?')
		return Conversions.str_to_bool(response)
