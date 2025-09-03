from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ClmnCls:
	"""Clmn commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("clmn", core, parent)

	def set(self, column: enums.Column, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""SBUS<*>:NRZC:FORMat:FRAMe<*>:FLD<*>:CLMN \n
		Snippet: driver.sbus.nrzc.formatPy.frame.fld.clmn.set(column = enums.Column.COL1, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies, in which result column of the decode table to display the selected field of the selected frame. \n
			:param column:
				- NONE: The result is not displayed.
				- COL1: The result is displayed in column 1.
				- COL2: The result is displayed in column 2.
				- COL3: The result is displayed in column 3.
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')"""
		param = Conversions.enum_scalar_to_str(column, enums.Column)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:CLMN {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.Column:
		"""SBUS<*>:NRZC:FORMat:FRAMe<*>:FLD<*>:CLMN \n
		Snippet: value: enums.Column = driver.sbus.nrzc.formatPy.frame.fld.clmn.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies, in which result column of the decode table to display the selected field of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: column:
				- NONE: The result is not displayed.
				- COL1: The result is displayed in column 1.
				- COL2: The result is displayed in column 2.
				- COL3: The result is displayed in column 3."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:CLMN?')
		return Conversions.str_to_scalar_enum(response, enums.Column)
