from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, source: enums.Source, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:SOURce \n
		Snippet: driver.cursor.source.set(source = enums.Source.C1, cursor = repcap.Cursor.Default) \n
		Selects the cursor source. \n
			:param source: No help available
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
		"""
		param = Conversions.enum_scalar_to_str(source, enums.Source)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, cursor=repcap.Cursor.Default) -> enums.Source:
		"""CURSor<*>:SOURce \n
		Snippet: value: enums.Source = driver.cursor.source.get(cursor = repcap.Cursor.Default) \n
		Selects the cursor source. \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: source: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
