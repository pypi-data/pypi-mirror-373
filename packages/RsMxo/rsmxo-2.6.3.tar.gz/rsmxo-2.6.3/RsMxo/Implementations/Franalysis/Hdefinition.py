from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HdefinitionCls:
	"""Hdefinition commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hdefinition", core, parent)

	def get_enable(self) -> bool:
		"""FRANalysis:HDEFinition[:ENABle] \n
		Snippet: value: bool = driver.franalysis.hdefinition.get_enable() \n
		No command help available \n
			:return: hd_mode: No help available
		"""
		response = self._core.io.query_str('FRANalysis:HDEFinition:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, hd_mode: bool) -> None:
		"""FRANalysis:HDEFinition[:ENABle] \n
		Snippet: driver.franalysis.hdefinition.set_enable(hd_mode = False) \n
		No command help available \n
			:param hd_mode: No help available
		"""
		param = Conversions.bool_to_str(hd_mode)
		self._core.io.write(f'FRANalysis:HDEFinition:ENABle {param}')
