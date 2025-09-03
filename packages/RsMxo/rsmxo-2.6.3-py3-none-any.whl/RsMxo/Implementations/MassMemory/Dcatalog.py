from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Types import DataType
from ...Internal.Utilities import trim_str_response
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DcatalogCls:
	"""Dcatalog commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dcatalog", core, parent)

	def get(self, path: str = None) -> str:
		"""MMEMory:DCATalog \n
		Snippet: value: str = driver.massMemory.dcatalog.get(path = 'abc') \n
		Returns the subdirectories of the current or of a specified directory. \n
			:param path: String parameter to specify the directory. If the directory is omitted, the command queries the contents of the current directory, to be set and queried with method RsMxo.MassMemory.currentDirectory.
			:return: directory: Names of the subdirectories separated by colons. The first two strings are related to the parent directory."""
		param = ArgSingleList().compose_cmd_string(ArgSingle('path', path, DataType.String, None, is_optional=True))
		response = self._core.io.query_str(f'MMEMory:DCATalog? {param}'.rstrip())
		return trim_str_response(response)
