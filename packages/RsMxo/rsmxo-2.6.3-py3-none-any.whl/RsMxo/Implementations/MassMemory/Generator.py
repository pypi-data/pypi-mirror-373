from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GeneratorCls:
	"""Generator commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("generator", core, parent)

	def get_save(self) -> str:
		"""MMEMory:GENerator:SAV \n
		Snippet: value: str = driver.massMemory.generator.get_save() \n
		Stores the current waveform generator settings to the specified file. \n
			:return: file_path: String parameter specifying path and filename of the settings file.
		"""
		response = self._core.io.query_str('MMEMory:GENerator:SAV?')
		return trim_str_response(response)

	def set_save(self, file_path: str) -> None:
		"""MMEMory:GENerator:SAV \n
		Snippet: driver.massMemory.generator.set_save(file_path = 'abc') \n
		Stores the current waveform generator settings to the specified file. \n
			:param file_path: String parameter specifying path and filename of the settings file.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'MMEMory:GENerator:SAV {param}')

	def get_recall(self) -> str:
		"""MMEMory:GENerator:RCL \n
		Snippet: value: str = driver.massMemory.generator.get_recall() \n
		Restores the waveform generator settings from the specified file. \n
			:return: file_path: String parameter specifying the path and filename of the settings file.
		"""
		response = self._core.io.query_str('MMEMory:GENerator:RCL?')
		return trim_str_response(response)

	def set_recall(self, file_path: str) -> None:
		"""MMEMory:GENerator:RCL \n
		Snippet: driver.massMemory.generator.set_recall(file_path = 'abc') \n
		Restores the waveform generator settings from the specified file. \n
			:param file_path: String parameter specifying the path and filename of the settings file.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'MMEMory:GENerator:RCL {param}')
