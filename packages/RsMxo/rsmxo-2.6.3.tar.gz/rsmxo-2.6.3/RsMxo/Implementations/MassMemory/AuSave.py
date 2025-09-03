from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AuSaveCls:
	"""AuSave commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("auSave", core, parent)

	def get_enable(self) -> bool:
		"""MMEMory:AUSave:ENABle \n
		Snippet: value: bool = driver.massMemory.auSave.get_enable() \n
		Enables the automatic saving of the waveform. You can set the autosave interval with method RsMxo.MassMemory.AuSave.
		interval. \n
			:return: enable_autosave: No help available
		"""
		response = self._core.io.query_str('MMEMory:AUSave:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable_autosave: bool) -> None:
		"""MMEMory:AUSave:ENABle \n
		Snippet: driver.massMemory.auSave.set_enable(enable_autosave = False) \n
		Enables the automatic saving of the waveform. You can set the autosave interval with method RsMxo.MassMemory.AuSave.
		interval. \n
			:param enable_autosave: No help available
		"""
		param = Conversions.bool_to_str(enable_autosave)
		self._core.io.write(f'MMEMory:AUSave:ENABle {param}')

	def get_interval(self) -> int:
		"""MMEMory:AUSave:INTerval \n
		Snippet: value: int = driver.massMemory.auSave.get_interval() \n
		Defines the time interval for the automatic saving of the waveform, if method RsMxo.MassMemory.AuSave.enable is set to ON. \n
			:return: autosave_interval: No help available
		"""
		response = self._core.io.query_str('MMEMory:AUSave:INTerval?')
		return Conversions.str_to_int(response)

	def set_interval(self, autosave_interval: int) -> None:
		"""MMEMory:AUSave:INTerval \n
		Snippet: driver.massMemory.auSave.set_interval(autosave_interval = 1) \n
		Defines the time interval for the automatic saving of the waveform, if method RsMxo.MassMemory.AuSave.enable is set to ON. \n
			:param autosave_interval: No help available
		"""
		param = Conversions.decimal_value_to_str(autosave_interval)
		self._core.io.write(f'MMEMory:AUSave:INTerval {param}')
