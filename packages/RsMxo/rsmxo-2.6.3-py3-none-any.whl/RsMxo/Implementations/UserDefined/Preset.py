from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PresetCls:
	"""Preset commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("preset", core, parent)

	def open(self, opc_timeout_ms: int = -1) -> None:
		"""USERdefined:PRESet:OPEN \n
		Snippet: driver.userDefined.preset.open() \n
		Opens and loads the preset file that is defined with method RsMxo.UserDefined.Preset.name. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'USERdefined:PRESet:OPEN', opc_timeout_ms)
		# OpcSyncAllowed = true

	def save(self, opc_timeout_ms: int = -1) -> None:
		"""USERdefined:PRESet:SAVE \n
		Snippet: driver.userDefined.preset.save() \n
		Saves the the current settings as a preset file. You define the storage location and filename with method RsMxo.
		UserDefined.Preset.name. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'USERdefined:PRESet:SAVE', opc_timeout_ms)
		# OpcSyncAllowed = true

	def get_enable(self) -> bool:
		"""USERdefined:PRESet[:ENABle] \n
		Snippet: value: bool = driver.userDefined.preset.get_enable() \n
		If enabled, the settings from the selected saveset are restored when the Preset key is pressed. If disabled, Preset sets
		the instrument to the factory defaults. The saveset to be used as preset file is defined with method RsMxo.UserDefined.
		Preset.name. \n
			:return: name: No help available
		"""
		response = self._core.io.query_str('USERdefined:PRESet:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, name: bool) -> None:
		"""USERdefined:PRESet[:ENABle] \n
		Snippet: driver.userDefined.preset.set_enable(name = False) \n
		If enabled, the settings from the selected saveset are restored when the Preset key is pressed. If disabled, Preset sets
		the instrument to the factory defaults. The saveset to be used as preset file is defined with method RsMxo.UserDefined.
		Preset.name. \n
			:param name: No help available
		"""
		param = Conversions.bool_to_str(name)
		self._core.io.write(f'USERdefined:PRESet:ENABle {param}')

	def get_name(self) -> str:
		"""USERdefined:PRESet:NAME \n
		Snippet: value: str = driver.userDefined.preset.get_name() \n
		Sets the path, the filename and the file format of the preset file. \n
			:return: name: String with path and file name with extension .set.
		"""
		response = self._core.io.query_str('USERdefined:PRESet:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""USERdefined:PRESet:NAME \n
		Snippet: driver.userDefined.preset.set_name(name = 'abc') \n
		Sets the path, the filename and the file format of the preset file. \n
			:param name: String with path and file name with extension .set.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'USERdefined:PRESet:NAME {param}')
