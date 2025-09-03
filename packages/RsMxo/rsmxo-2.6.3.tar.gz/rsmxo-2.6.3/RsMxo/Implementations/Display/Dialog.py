from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DialogCls:
	"""Dialog commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dialog", core, parent)

	def get_fontsize(self) -> int:
		"""DISPlay:DIALog:FONTsize \n
		Snippet: value: int = driver.display.dialog.get_fontsize() \n
		Sets the font size of the text in dialog boxes. \n
			:return: dialog_font_size: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIALog:FONTsize?')
		return Conversions.str_to_int(response)

	def set_fontsize(self, dialog_font_size: int) -> None:
		"""DISPlay:DIALog:FONTsize \n
		Snippet: driver.display.dialog.set_fontsize(dialog_font_size = 1) \n
		Sets the font size of the text in dialog boxes. \n
			:param dialog_font_size: No help available
		"""
		param = Conversions.decimal_value_to_str(dialog_font_size)
		self._core.io.write(f'DISPlay:DIALog:FONTsize {param}')

	def get_transparency(self) -> int:
		"""DISPlay:DIALog:TRANsparency \n
		Snippet: value: int = driver.display.dialog.get_transparency() \n
		Sets the transparency of the dialog box background. For high transparency values, you can see the waveform display in the
		background, and possibly check the effect of the changed setting. For lower transparency values, readability in the
		dialog box improves. \n
			:return: dialog_transp: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIALog:TRANsparency?')
		return Conversions.str_to_int(response)

	def set_transparency(self, dialog_transp: int) -> None:
		"""DISPlay:DIALog:TRANsparency \n
		Snippet: driver.display.dialog.set_transparency(dialog_transp = 1) \n
		Sets the transparency of the dialog box background. For high transparency values, you can see the waveform display in the
		background, and possibly check the effect of the changed setting. For lower transparency values, readability in the
		dialog box improves. \n
			:param dialog_transp: No help available
		"""
		param = Conversions.decimal_value_to_str(dialog_transp)
		self._core.io.write(f'DISPlay:DIALog:TRANsparency {param}')
