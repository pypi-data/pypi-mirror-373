from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AutoNamingCls:
	"""AutoNaming commands group definition. 8 total commands, 2 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("autoNaming", core, parent)

	@property
	def resPath(self):
		"""resPath commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_resPath'):
			from .ResPath import ResPathCls
			self._resPath = ResPathCls(self._core, self._cmd_group)
		return self._resPath

	@property
	def resAll(self):
		"""resAll commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_resAll'):
			from .ResAll import ResAllCls
			self._resAll = ResAllCls(self._core, self._cmd_group)
		return self._resAll

	def get_time(self) -> bool:
		"""MMEMory:AUTonaming:TIME \n
		Snippet: value: bool = driver.massMemory.autoNaming.get_time() \n
		Includes or excludes the prefix/ date/time /index in the filename pattern for automatic filename generation. This name is
		used as the default filename. The prefix indicates the type of data that is saved, for example, RefCurve, Settings. \n
			:return: name_date_time: No help available
		"""
		response = self._core.io.query_str('MMEMory:AUTonaming:TIME?')
		return Conversions.str_to_bool(response)

	def set_time(self, name_date_time: bool) -> None:
		"""MMEMory:AUTonaming:TIME \n
		Snippet: driver.massMemory.autoNaming.set_time(name_date_time = False) \n
		Includes or excludes the prefix/ date/time /index in the filename pattern for automatic filename generation. This name is
		used as the default filename. The prefix indicates the type of data that is saved, for example, RefCurve, Settings. \n
			:param name_date_time: No help available
		"""
		param = Conversions.bool_to_str(name_date_time)
		self._core.io.write(f'MMEMory:AUTonaming:TIME {param}')

	def get_index(self) -> bool:
		"""MMEMory:AUTonaming:INDex \n
		Snippet: value: bool = driver.massMemory.autoNaming.get_index() \n
		Includes or excludes the prefix/ date/time /index in the filename pattern for automatic filename generation. This name is
		used as the default filename. The prefix indicates the type of data that is saved, for example, RefCurve, Settings. \n
			:return: name_index: No help available
		"""
		response = self._core.io.query_str('MMEMory:AUTonaming:INDex?')
		return Conversions.str_to_bool(response)

	def set_index(self, name_index: bool) -> None:
		"""MMEMory:AUTonaming:INDex \n
		Snippet: driver.massMemory.autoNaming.set_index(name_index = False) \n
		Includes or excludes the prefix/ date/time /index in the filename pattern for automatic filename generation. This name is
		used as the default filename. The prefix indicates the type of data that is saved, for example, RefCurve, Settings. \n
			:param name_index: No help available
		"""
		param = Conversions.bool_to_str(name_index)
		self._core.io.write(f'MMEMory:AUTonaming:INDex {param}')

	def get_user_text(self) -> bool:
		"""MMEMory:AUTonaming:USERtext \n
		Snippet: value: bool = driver.massMemory.autoNaming.get_user_text() \n
		If enabled, inserts the specified user text after the prefix. You can define the text with method RsMxo.MassMemory.
		AutoNaming.text. \n
			:return: nme_string_st: No help available
		"""
		response = self._core.io.query_str('MMEMory:AUTonaming:USERtext?')
		return Conversions.str_to_bool(response)

	def set_user_text(self, nme_string_st: bool) -> None:
		"""MMEMory:AUTonaming:USERtext \n
		Snippet: driver.massMemory.autoNaming.set_user_text(nme_string_st = False) \n
		If enabled, inserts the specified user text after the prefix. You can define the text with method RsMxo.MassMemory.
		AutoNaming.text. \n
			:param nme_string_st: No help available
		"""
		param = Conversions.bool_to_str(nme_string_st)
		self._core.io.write(f'MMEMory:AUTonaming:USERtext {param}')

	def get_prefix(self) -> bool:
		"""MMEMory:AUTonaming:PREFix \n
		Snippet: value: bool = driver.massMemory.autoNaming.get_prefix() \n
		Includes or excludes the prefix/ date/time /index in the filename pattern for automatic filename generation. This name is
		used as the default filename. The prefix indicates the type of data that is saved, for example, RefCurve, Settings. \n
			:return: main_nme_stem_st: No help available
		"""
		response = self._core.io.query_str('MMEMory:AUTonaming:PREFix?')
		return Conversions.str_to_bool(response)

	def set_prefix(self, main_nme_stem_st: bool) -> None:
		"""MMEMory:AUTonaming:PREFix \n
		Snippet: driver.massMemory.autoNaming.set_prefix(main_nme_stem_st = False) \n
		Includes or excludes the prefix/ date/time /index in the filename pattern for automatic filename generation. This name is
		used as the default filename. The prefix indicates the type of data that is saved, for example, RefCurve, Settings. \n
			:param main_nme_stem_st: No help available
		"""
		param = Conversions.bool_to_str(main_nme_stem_st)
		self._core.io.write(f'MMEMory:AUTonaming:PREFix {param}')

	def get_text(self) -> str:
		"""MMEMory:AUTonaming:TEXT \n
		Snippet: value: str = driver.massMemory.autoNaming.get_text() \n
		Defines a text that can be included in the autonaming pattern. \n
			:return: name_string: String parameter
		"""
		response = self._core.io.query_str('MMEMory:AUTonaming:TEXT?')
		return trim_str_response(response)

	def set_text(self, name_string: str) -> None:
		"""MMEMory:AUTonaming:TEXT \n
		Snippet: driver.massMemory.autoNaming.set_text(name_string = 'abc') \n
		Defines a text that can be included in the autonaming pattern. \n
			:param name_string: String parameter
		"""
		param = Conversions.value_to_quoted_str(name_string)
		self._core.io.write(f'MMEMory:AUTonaming:TEXT {param}')

	def get_default_path(self) -> str:
		"""MMEMory:AUTonaming:DEFaultpath \n
		Snippet: value: str = driver.massMemory.autoNaming.get_default_path() \n
		Sets the path where data and settings files are stored. On the instrument, all user data is written to
		/home/storage/userData. You can create subfolders in this folder. \n
			:return: path: String parameter
		"""
		response = self._core.io.query_str('MMEMory:AUTonaming:DEFaultpath?')
		return trim_str_response(response)

	def set_default_path(self, path: str) -> None:
		"""MMEMory:AUTonaming:DEFaultpath \n
		Snippet: driver.massMemory.autoNaming.set_default_path(path = 'abc') \n
		Sets the path where data and settings files are stored. On the instrument, all user data is written to
		/home/storage/userData. You can create subfolders in this folder. \n
			:param path: String parameter
		"""
		param = Conversions.value_to_quoted_str(path)
		self._core.io.write(f'MMEMory:AUTonaming:DEFaultpath {param}')

	def clone(self) -> 'AutoNamingCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AutoNamingCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
