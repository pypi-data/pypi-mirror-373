from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SyncCls:
	"""Sync commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sync", core, parent)

	# noinspection PyTypeChecker
	def get_combination(self) -> enums.GenSyncCombination:
		"""GENerator:SYNC[:COMBination] \n
		Snippet: value: enums.GenSyncCombination = driver.generator.sync.get_combination() \n
		Selects which signals generated from the waveform generator are synchronized. \n
			:return: combination: No help available
		"""
		response = self._core.io.query_str('GENerator:SYNC:COMBination?')
		return Conversions.str_to_scalar_enum(response, enums.GenSyncCombination)

	def set_combination(self, combination: enums.GenSyncCombination) -> None:
		"""GENerator:SYNC[:COMBination] \n
		Snippet: driver.generator.sync.set_combination(combination = enums.GenSyncCombination.GEN12) \n
		Selects which signals generated from the waveform generator are synchronized. \n
			:param combination: No help available
		"""
		param = Conversions.enum_scalar_to_str(combination, enums.GenSyncCombination)
		self._core.io.write(f'GENerator:SYNC:COMBination {param}')
