from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ConfigCls:
	"""Config commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("config", core, parent)

	def get_preview(self) -> bool:
		"""SAVeset:CONFig:PREView \n
		Snippet: value: bool = driver.saveset.config.get_preview() \n
		If set to OFF, the saveset is stored without the preview image to reduce the file size. Use the command each time before
		you save a saveset. \n
			:return: include_preview_image_in_saveset: No help available
		"""
		response = self._core.io.query_str('SAVeset:CONFig:PREView?')
		return Conversions.str_to_bool(response)

	def set_preview(self, include_preview_image_in_saveset: bool) -> None:
		"""SAVeset:CONFig:PREView \n
		Snippet: driver.saveset.config.set_preview(include_preview_image_in_saveset = False) \n
		If set to OFF, the saveset is stored without the preview image to reduce the file size. Use the command each time before
		you save a saveset. \n
			:param include_preview_image_in_saveset: No help available
		"""
		param = Conversions.bool_to_str(include_preview_image_in_saveset)
		self._core.io.write(f'SAVeset:CONFig:PREView {param}')

	def get_upreferences(self) -> bool:
		"""SAVeset:CONFig:UPReferences \n
		Snippet: value: bool = driver.saveset.config.get_upreferences() \n
		If ON, the user-specific display settings for the toolbar, waveform colors and diagram presentation are included in the
		saveset file. The setting affects the saving and the recall actions. \n
			:return: recall_include_user_setting: No help available
		"""
		response = self._core.io.query_str('SAVeset:CONFig:UPReferences?')
		return Conversions.str_to_bool(response)

	def set_upreferences(self, recall_include_user_setting: bool) -> None:
		"""SAVeset:CONFig:UPReferences \n
		Snippet: driver.saveset.config.set_upreferences(recall_include_user_setting = False) \n
		If ON, the user-specific display settings for the toolbar, waveform colors and diagram presentation are included in the
		saveset file. The setting affects the saving and the recall actions. \n
			:param recall_include_user_setting: No help available
		"""
		param = Conversions.bool_to_str(recall_include_user_setting)
		self._core.io.write(f'SAVeset:CONFig:UPReferences {param}')
