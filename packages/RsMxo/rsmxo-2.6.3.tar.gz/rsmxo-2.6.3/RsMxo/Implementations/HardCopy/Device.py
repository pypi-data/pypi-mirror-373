from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DeviceCls:
	"""Device commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("device", core, parent)

	# noinspection PyTypeChecker
	def get_language(self) -> enums.PictureFileFormat:
		"""HCOPy:DEVice:LANGuage \n
		Snippet: value: enums.PictureFileFormat = driver.hardCopy.device.get_language() \n
		Defines the file format for output of the screenshot to file. To set the output to file, use HCOPy:DESTination<m> with
		parameter MMEM. \n
			:return: file_format: No help available
		"""
		response = self._core.io.query_str('HCOPy:DEVice:LANGuage?')
		return Conversions.str_to_scalar_enum(response, enums.PictureFileFormat)

	def set_language(self, file_format: enums.PictureFileFormat) -> None:
		"""HCOPy:DEVice:LANGuage \n
		Snippet: driver.hardCopy.device.set_language(file_format = enums.PictureFileFormat.BMP) \n
		Defines the file format for output of the screenshot to file. To set the output to file, use HCOPy:DESTination<m> with
		parameter MMEM. \n
			:param file_format: No help available
		"""
		param = Conversions.enum_scalar_to_str(file_format, enums.PictureFileFormat)
		self._core.io.write(f'HCOPy:DEVice:LANGuage {param}')

	def get_inverse(self) -> bool:
		"""HCOPy:DEVice:INVerse \n
		Snippet: value: bool = driver.hardCopy.device.get_inverse() \n
		Inverts the colors of the output, i.e. a dark waveform is shown on a white background. See also method RsMxo.HardCopy.
		wbkg and 'White background'. \n
			:return: inverse_color: No help available
		"""
		response = self._core.io.query_str('HCOPy:DEVice:INVerse?')
		return Conversions.str_to_bool(response)

	def set_inverse(self, inverse_color: bool) -> None:
		"""HCOPy:DEVice:INVerse \n
		Snippet: driver.hardCopy.device.set_inverse(inverse_color = False) \n
		Inverts the colors of the output, i.e. a dark waveform is shown on a white background. See also method RsMxo.HardCopy.
		wbkg and 'White background'. \n
			:param inverse_color: No help available
		"""
		param = Conversions.bool_to_str(inverse_color)
		self._core.io.write(f'HCOPy:DEVice:INVerse {param}')
