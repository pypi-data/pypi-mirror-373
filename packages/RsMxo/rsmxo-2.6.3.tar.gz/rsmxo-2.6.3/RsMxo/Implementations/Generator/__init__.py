from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GeneratorCls:
	"""Generator commands group definition. 6 total commands, 2 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("generator", core, parent)

	@property
	def sync(self):
		"""sync commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sync'):
			from .Sync import SyncCls
			self._sync = SyncCls(self._core, self._cmd_group)
		return self._sync

	@property
	def alignment(self):
		"""alignment commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_alignment'):
			from .Alignment import AlignmentCls
			self._alignment = AlignmentCls(self._core, self._cmd_group)
		return self._alignment

	def get_save(self) -> str:
		"""GENerator:SAV \n
		Snippet: value: str = driver.generator.get_save() \n
		Stores the current waveform generator settings to the specified file. \n
			:return: file_path: String parameter specifying path and filename of the target file.
		"""
		response = self._core.io.query_str('GENerator:SAV?')
		return trim_str_response(response)

	def set_save(self, file_path: str) -> None:
		"""GENerator:SAV \n
		Snippet: driver.generator.set_save(file_path = 'abc') \n
		Stores the current waveform generator settings to the specified file. \n
			:param file_path: String parameter specifying path and filename of the target file.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'GENerator:SAV {param}')

	def get_recall(self) -> str:
		"""GENerator:RCL \n
		Snippet: value: str = driver.generator.get_recall() \n
		Restores the waveform generator from the specified file. \n
			:return: file_path: String parameter specifying the path and filename of the source file.
		"""
		response = self._core.io.query_str('GENerator:RCL?')
		return trim_str_response(response)

	def set_recall(self, file_path: str) -> None:
		"""GENerator:RCL \n
		Snippet: driver.generator.set_recall(file_path = 'abc') \n
		Restores the waveform generator from the specified file. \n
			:param file_path: String parameter specifying the path and filename of the source file.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'GENerator:RCL {param}')

	def clone(self) -> 'GeneratorCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = GeneratorCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
