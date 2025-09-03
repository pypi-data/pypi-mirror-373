from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup
from ..Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TrfsCls:
	"""Trfs commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("trfs", core, parent)

	def get_count(self) -> int:
		"""TRFS:COUNt \n
		Snippet: value: int = driver.trfs.get_count() \n
		Returns the number of defined timing references. \n
			:return: count: No help available
		"""
		response = self._core.io.query_str('TRFS:COUNt?')
		return Conversions.str_to_int(response)
