from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Types import DataType
from ...Internal.StructBase import StructBase
from ...Internal.ArgStruct import ArgStruct
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DataCls:
	"""Data commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	def set(self, format_py: enums.DataFormat = None, length: int = None) -> None:
		"""FORMat[:DATA] \n
		Snippet: driver.formatPy.data.set(format_py = enums.DataFormat.ASCii, length = 1) \n
		Selects the data type that is used for transmission of data from analog channels, math and reference waveforms, and some
		measurement results from the instrument to the controlling computer. For INT and REAL formats, use method RsMxo.FormatPy.
		border to set the byte order. If you need physical data (e.g. in Volt or Ampere) for further analysis, use the floating
		point formats (REAL) for export. No data conversion is needed. \n
			:param format_py:
				- ASCii: Data values are returned in ASCII format as a list of comma-separated values in floating point format. The length can be omitted. It is 0 which means that the instrument selects the number of digits to be returned. The query returns both values (ASC,0) .
				- REAL,32: FLOAT, physical data in floating point format. The data is stored as binary data (Definite Length Block Data according to IEEE 488.2) . Each waveform value is formatted in the 32-Bit IEEE 754 floating point format.The schema of the result string is as follows: #41024value1value2…value n with:#4 = number of digits (= 4 in the example) of the following number1024 = number of following data bytes (= 1024 in the example) value = 4-byte floating point valuesFor large data (≥ 1 GB) , the result string starts with '#(data length) '. The number inside the parentheses indicates the real data length in bytes.
				- REAL,64: DOUBLE format, 64 bit floating point format.
				- INT,8 | INT,16 | INT,32: Signed integer data with length 8 bit, 16 bit, or 32 bit.The result string has the same schema as the REAL format.For INT,16, you can set the byte order using the command.For digital channel data, math and histogram data, INT formats are not available.
			:param length:
				- ASCii: Data values are returned in ASCII format as a list of comma-separated values in floating point format. The length can be omitted. It is 0 which means that the instrument selects the number of digits to be returned. The query returns both values (ASC,0) .
				- REAL,32: FLOAT, physical data in floating point format. The data is stored as binary data (Definite Length Block Data according to IEEE 488.2) . Each waveform value is formatted in the 32-Bit IEEE 754 floating point format.The schema of the result string is as follows: #41024value1value2…value n with:#4 = number of digits (= 4 in the example) of the following number1024 = number of following data bytes (= 1024 in the example) value = 4-byte floating point valuesFor large data (≥ 1 GB) , the result string starts with '#(data length) '. The number inside the parentheses indicates the real data length in bytes.
				- REAL,64: DOUBLE format, 64 bit floating point format.
				- INT,8 | INT,16 | INT,32: Signed integer data with length 8 bit, 16 bit, or 32 bit.The result string has the same schema as the REAL format.For INT,16, you can set the byte order using the command.For digital channel data, math and histogram data, INT formats are not available."""
		param = ArgSingleList().compose_cmd_string(ArgSingle('format_py', format_py, DataType.Enum, enums.DataFormat, is_optional=True), ArgSingle('length', length, DataType.Integer, None, is_optional=True))
		self._core.io.write(f'FORMat:DATA {param}'.rstrip())

	# noinspection PyTypeChecker
	class DataStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Format_Py: enums.DataFormat:
				- ASCii: Data values are returned in ASCII format as a list of comma-separated values in floating point format. The length can be omitted. It is 0 which means that the instrument selects the number of digits to be returned. The query returns both values (ASC,0) .
				- REAL,32: FLOAT, physical data in floating point format. The data is stored as binary data (Definite Length Block Data according to IEEE 488.2) . Each waveform value is formatted in the 32-Bit IEEE 754 floating point format.The schema of the result string is as follows: #41024value1value2…value n with:#4 = number of digits (= 4 in the example) of the following number1024 = number of following data bytes (= 1024 in the example) value = 4-byte floating point valuesFor large data (≥ 1 GB) , the result string starts with '#(data length) '. The number inside the parentheses indicates the real data length in bytes.
				- REAL,64: DOUBLE format, 64 bit floating point format.
				- INT,8 | INT,16 | INT,32: Signed integer data with length 8 bit, 16 bit, or 32 bit.The result string has the same schema as the REAL format.For INT,16, you can set the byte order using the command.For digital channel data, math and histogram data, INT formats are not available.
			- 2 Length: int:
				- ASCii: Data values are returned in ASCII format as a list of comma-separated values in floating point format. The length can be omitted. It is 0 which means that the instrument selects the number of digits to be returned. The query returns both values (ASC,0) .
				- REAL,32: FLOAT, physical data in floating point format. The data is stored as binary data (Definite Length Block Data according to IEEE 488.2) . Each waveform value is formatted in the 32-Bit IEEE 754 floating point format.The schema of the result string is as follows: #41024value1value2…value n with:#4 = number of digits (= 4 in the example) of the following number1024 = number of following data bytes (= 1024 in the example) value = 4-byte floating point valuesFor large data (≥ 1 GB) , the result string starts with '#(data length) '. The number inside the parentheses indicates the real data length in bytes.
				- REAL,64: DOUBLE format, 64 bit floating point format.
				- INT,8 | INT,16 | INT,32: Signed integer data with length 8 bit, 16 bit, or 32 bit.The result string has the same schema as the REAL format.For INT,16, you can set the byte order using the command.For digital channel data, math and histogram data, INT formats are not available."""
		__meta_args_list = [
			ArgStruct.scalar_enum('Format_Py', enums.DataFormat),
			ArgStruct.scalar_int('Length')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Format_Py: enums.DataFormat = None
			self.Length: int = None

	def get(self) -> DataStruct:
		"""FORMat[:DATA] \n
		Snippet: value: DataStruct = driver.formatPy.data.get() \n
		Selects the data type that is used for transmission of data from analog channels, math and reference waveforms, and some
		measurement results from the instrument to the controlling computer. For INT and REAL formats, use method RsMxo.FormatPy.
		border to set the byte order. If you need physical data (e.g. in Volt or Ampere) for further analysis, use the floating
		point formats (REAL) for export. No data conversion is needed. \n
			:return: structure: for return value, see the help for DataStruct structure arguments."""
		return self._core.io.query_struct(f'FORMat:DATA?', self.__class__.DataStruct())
