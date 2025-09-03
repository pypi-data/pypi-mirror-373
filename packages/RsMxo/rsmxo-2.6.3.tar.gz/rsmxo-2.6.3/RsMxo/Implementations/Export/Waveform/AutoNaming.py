from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AutoNamingCls:
	"""AutoNaming commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("autoNaming", core, parent)

	def get_name(self) -> str:
		"""EXPort:WAVeform:AUTonaming:NAME \n
		Snippet: value: str = driver.export.waveform.autoNaming.get_name() \n
		Sets a name for the waveform file, without extension. The name is extended with a time stamp when the file is saved. The
		setting is used for automatic saving actions, for example, saving on trigger or mask violation. It has no effect on
		method RsMxo.Export.Waveform.save. \n
			:return: filename: String with the filename.
		"""
		response = self._core.io.query_str('EXPort:WAVeform:AUTonaming:NAME?')
		return trim_str_response(response)

	def set_name(self, filename: str) -> None:
		"""EXPort:WAVeform:AUTonaming:NAME \n
		Snippet: driver.export.waveform.autoNaming.set_name(filename = 'abc') \n
		Sets a name for the waveform file, without extension. The name is extended with a time stamp when the file is saved. The
		setting is used for automatic saving actions, for example, saving on trigger or mask violation. It has no effect on
		method RsMxo.Export.Waveform.save. \n
			:param filename: String with the filename.
		"""
		param = Conversions.value_to_quoted_str(filename)
		self._core.io.write(f'EXPort:WAVeform:AUTonaming:NAME {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.FileExtension:
		"""EXPort:WAVeform:AUTonaming:TYPE \n
		Snippet: value: enums.FileExtension = driver.export.waveform.autoNaming.get_type_py() \n
		Sets the file type of the waveform file. The setting is used for automatic saving actions, for example, saving on trigger
		or mask violation. It has no effect on method RsMxo.Export.Waveform.save. \n
			:return: file_extension: No help available
		"""
		response = self._core.io.query_str('EXPort:WAVeform:AUTonaming:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.FileExtension)

	def set_type_py(self, file_extension: enums.FileExtension) -> None:
		"""EXPort:WAVeform:AUTonaming:TYPE \n
		Snippet: driver.export.waveform.autoNaming.set_type_py(file_extension = enums.FileExtension.BIN) \n
		Sets the file type of the waveform file. The setting is used for automatic saving actions, for example, saving on trigger
		or mask violation. It has no effect on method RsMxo.Export.Waveform.save. \n
			:param file_extension: No help available
		"""
		param = Conversions.enum_scalar_to_str(file_extension, enums.FileExtension)
		self._core.io.write(f'EXPort:WAVeform:AUTonaming:TYPE {param}')

	def get_path(self) -> str:
		"""EXPort:WAVeform:AUTonaming:PATH \n
		Snippet: value: str = driver.export.waveform.autoNaming.get_path() \n
		Sets the directory where the waveform file is saved. For local storage, the path is always /home/storage/userData.
		The setting is used for automatic saving actions, for example, saving on trigger or mask violation. It has no effect on
		method RsMxo.Export.Waveform.save. \n
			:return: folder_path: String with the path.
		"""
		response = self._core.io.query_str('EXPort:WAVeform:AUTonaming:PATH?')
		return trim_str_response(response)

	def set_path(self, folder_path: str) -> None:
		"""EXPort:WAVeform:AUTonaming:PATH \n
		Snippet: driver.export.waveform.autoNaming.set_path(folder_path = 'abc') \n
		Sets the directory where the waveform file is saved. For local storage, the path is always /home/storage/userData.
		The setting is used for automatic saving actions, for example, saving on trigger or mask violation. It has no effect on
		method RsMxo.Export.Waveform.save. \n
			:param folder_path: String with the path.
		"""
		param = Conversions.value_to_quoted_str(folder_path)
		self._core.io.write(f'EXPort:WAVeform:AUTonaming:PATH {param}')
