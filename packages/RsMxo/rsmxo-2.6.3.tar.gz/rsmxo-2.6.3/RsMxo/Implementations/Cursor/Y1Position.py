from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Y1PositionCls:
	"""Y1Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("y1Position", core, parent)

	def set(self, yposition_1: float, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:Y1Position \n
		Snippet: driver.cursor.y1Position.set(yposition_1 = 1.0, cursor = repcap.Cursor.Default) \n
		Defines the position of the lower horizontal cursor line. If method RsMxo.Cursor.Tracking.State.set is enabled, the
		y-positions are set automatically. The query returns the measurement result - the lower vertical value of the waveform. \n
			:param yposition_1: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.decimal_value_to_str(yposition_1)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:Y1Position {param}')

	def get(self, cursor=repcap.Cursor.Default) -> float:
		"""CURSor<*>:Y1Position \n
		Snippet: value: float = driver.cursor.y1Position.get(cursor = repcap.Cursor.Default) \n
		Defines the position of the lower horizontal cursor line. If method RsMxo.Cursor.Tracking.State.set is enabled, the
		y-positions are set automatically. The query returns the measurement result - the lower vertical value of the waveform. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: yposition_1: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:Y1Position?')
		return Conversions.str_to_float(response)
