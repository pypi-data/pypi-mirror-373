from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FormatPyCls:
	"""FormatPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("formatPy", core, parent)

	def set(self, numeric_format: enums.SbusDataFormat, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:FLD<*>:FORMat \n
		Snippet: driver.sbus.nrzu.formatPy.frame.fld.formatPy.set(numeric_format = enums.SbusDataFormat.ASCII, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the numerical format for the condition value of the selected field in the selected frame. \n
			:param numeric_format:
				- DEC: Decimal format
				- HEX: Hexadecimal format
				- OCT: Octal format
				- BIN: Binary format
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')"""
		param = Conversions.enum_scalar_to_str(numeric_format, enums.SbusDataFormat)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:FORMat {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.SbusDataFormat:
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:FLD<*>:FORMat \n
		Snippet: value: enums.SbusDataFormat = driver.sbus.nrzu.formatPy.frame.fld.formatPy.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the numerical format for the condition value of the selected field in the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: numeric_format:
				- DEC: Decimal format
				- HEX: Hexadecimal format
				- OCT: Octal format
				- BIN: Binary format"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:FORMat?')
		return Conversions.str_to_scalar_enum(response, enums.SbusDataFormat)
