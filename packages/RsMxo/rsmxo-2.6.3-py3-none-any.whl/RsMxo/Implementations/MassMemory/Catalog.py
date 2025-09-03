from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Types import DataType
from ...Internal.Utilities import trim_str_response
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CatalogCls:
	"""Catalog commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("catalog", core, parent)

	def get(self, path: str = None) -> str:
		"""MMEMory:CATalog \n
		Snippet: value: str = driver.massMemory.catalog.get(path = 'abc') \n
		Returns a list of files contained in the specified directory. The result corresponds to the number of files returned by
		the MMEMory:CATalog:LENgth command. \n
			:param path: No help available
			:return: catalog: No help available"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('path', path, DataType.String, None, is_optional=True))
		response = self._core.io.query_str(f'MMEMory:CATalog? {param}'.rstrip())
		return trim_str_response(response)
