from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Types import DataType
from ...Internal.Utilities import trim_str_response
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MassMemoryCls:
	"""MassMemory commands group definition. 26 total commands, 7 Subgroups, 10 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("massMemory", core, parent)

	@property
	def catalog(self):
		"""catalog commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_catalog'):
			from .Catalog import CatalogCls
			self._catalog = CatalogCls(self._core, self._cmd_group)
		return self._catalog

	@property
	def dcatalog(self):
		"""dcatalog commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dcatalog'):
			from .Dcatalog import DcatalogCls
			self._dcatalog = DcatalogCls(self._core, self._cmd_group)
		return self._dcatalog

	@property
	def load(self):
		"""load commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_load'):
			from .Load import LoadCls
			self._load = LoadCls(self._core, self._cmd_group)
		return self._load

	@property
	def store(self):
		"""store commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_store'):
			from .Store import StoreCls
			self._store = StoreCls(self._core, self._cmd_group)
		return self._store

	@property
	def autoNaming(self):
		"""autoNaming commands group. 2 Sub-classes, 6 commands."""
		if not hasattr(self, '_autoNaming'):
			from .AutoNaming import AutoNamingCls
			self._autoNaming = AutoNamingCls(self._core, self._cmd_group)
		return self._autoNaming

	@property
	def auSave(self):
		"""auSave commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_auSave'):
			from .AuSave import AuSaveCls
			self._auSave = AuSaveCls(self._core, self._cmd_group)
		return self._auSave

	@property
	def generator(self):
		"""generator commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_generator'):
			from .Generator import GeneratorCls
			self._generator = GeneratorCls(self._core, self._cmd_group)
		return self._generator

	def get_current_directory(self) -> str:
		"""MMEMory:CDIRectory \n
		Snippet: value: str = driver.massMemory.get_current_directory() \n
		Changes the default directory for file access. \n
			:return: directory: No help available
		"""
		response = self._core.io.query_str('MMEMory:CDIRectory?')
		return trim_str_response(response)

	def set_current_directory(self, directory: str) -> None:
		"""MMEMory:CDIRectory \n
		Snippet: driver.massMemory.set_current_directory(directory = 'abc') \n
		Changes the default directory for file access. \n
			:param directory: String parameter to specify the directory.
		"""
		param = Conversions.value_to_quoted_str(directory)
		self._core.io.write(f'MMEMory:CDIRectory {param}')

	def delete(self, file_path: str) -> None:
		"""MMEMory:DELete \n
		Snippet: driver.massMemory.delete(file_path = 'abc') \n
		Removes the specified file/files. To delete directories, use method RsMxo.MassMemory.deleteDirectory. \n
			:param file_path: String parameter to specify the name and directory of the file to be removed. Wildcards (* and ?) are allowed. If no path is defined, the current directory is used, specified with method RsMxo.MassMemory.currentDirectory.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write_with_opc(f'MMEMory:DELete {param}')

	def delete_directory(self, directory_path: str) -> None:
		"""MMEMory:RDIRectory \n
		Snippet: driver.massMemory.delete_directory(directory_path = 'abc') \n
		Deletes the specified directory. \n
			:param directory_path: String parameter to specify the directory to be deleted. This directory must be empty, otherwise it is not deleted.
		"""
		param = Conversions.value_to_quoted_str(directory_path)
		self._core.io.write_with_opc(f'MMEMory:RDIRectory {param}')

	def copy(self, source: str, target: str) -> None:
		"""MMEMory:COPY \n
		Snippet: driver.massMemory.copy(source = 'abc', target = 'abc') \n
		Copies an existing file to a new file. \n
			:param source: No help available
			:param target: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('source', source, DataType.String), ArgSingle('target', target, DataType.String))
		self._core.io.write_with_opc(f'MMEMory:COPY {param}'.rstrip())

	def move(self, source: str, target: str) -> None:
		"""MMEMory:MOVE \n
		Snippet: driver.massMemory.move(source = 'abc', target = 'abc') \n
		Moves the specified file to a new location on the same drive and renames it. \n
			:param source: No help available
			:param target: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('source', source, DataType.String), ArgSingle('target', target, DataType.String))
		self._core.io.write_with_opc(f'MMEMory:MOVE {param}'.rstrip())

	def make_directory(self, directory_name: str) -> None:
		"""MMEMory:MDIRectory \n
		Snippet: driver.massMemory.make_directory(directory_name = 'abc') \n
		Creates a new directory with the specified name. \n
			:param directory_name: String parameter to specify the new directory. If the path consists of several subdirectories, the complete tree is created if necessary.
		"""
		param = Conversions.value_to_quoted_str(directory_name)
		self._core.io.write_with_opc(f'MMEMory:MDIRectory {param}')

	def save(self, file_destination: str) -> None:
		"""MMEMory:SAV \n
		Snippet: driver.massMemory.save(file_destination = 'abc') \n
		Stores the current instrument settings to the specified file. Waveform generator settings are not included. This command
		has the same effect as the combination of *SAV and method RsMxo.MassMemory.Store.State.set. \n
			:param file_destination: String parameter specifying path and filename of the target file. Wildcards are not allowed.
		"""
		param = Conversions.value_to_quoted_str(file_destination)
		self._core.io.write_with_opc(f'MMEMory:SAV {param}')

	def recall(self, file_source: str) -> None:
		"""MMEMory:RCL \n
		Snippet: driver.massMemory.recall(file_source = 'abc') \n
		Restores the instrument settings from the specified file. The stored instrument settings do not include waveform
		generator settings. This command has the same effect as the combination of method RsMxo.MassMemory.Load.State.
		set and *RCL. \n
			:param file_source: No help available
		"""
		param = Conversions.value_to_quoted_str(file_source)
		self._core.io.write_with_opc(f'MMEMory:RCL {param}')

	def get_name(self) -> str:
		"""MMEMory:NAME \n
		Snippet: value: str = driver.massMemory.get_name() \n
		Defines the filename for a screenshot that is stored to a file. \n
			:return: filename: String parameter specifying path and filename of the screenshot.
		"""
		response = self._core.io.query_str('MMEMory:NAME?')
		return trim_str_response(response)

	def set_name(self, filename: str) -> None:
		"""MMEMory:NAME \n
		Snippet: driver.massMemory.set_name(filename = 'abc') \n
		Defines the filename for a screenshot that is stored to a file. \n
			:param filename: String parameter specifying path and filename of the screenshot.
		"""
		param = Conversions.value_to_quoted_str(filename)
		self._core.io.write(f'MMEMory:NAME {param}')

	def get_drives(self) -> str:
		"""MMEMory:DRIVes \n
		Snippet: value: str = driver.massMemory.get_drives() \n
		Returns the path list of available drives. \n
			:return: drives: List of strings, for example: Instrument only: '/home/storage/userData' Instrument with connected USB flash drive: '/home/storage/userData','/run/media/usb/MyDriveName/MYDATA'. MYDATA is the partition name, which is also shown in the file explorer. Instrument with connected USB flash drive: '/home/storage/userData','/run/media/usb/MyDriveName/8AF8-3EBA'. 8AF8-3EBA is an example ID. ID is used if the partition does not have a name, or the name cannot be read.
		"""
		response = self._core.io.query_str('MMEMory:DRIVes?')
		return trim_str_response(response)

	def clone(self) -> 'MassMemoryCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MassMemoryCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
