from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RollCls:
	"""Roll commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("roll", core, parent)

	# noinspection PyTypeChecker
	def get_enable(self) -> enums.TimebaseRollMode:
		"""TIMebase:ROLL:ENABle \n
		Snippet: value: enums.TimebaseRollMode = driver.timebase.roll.get_enable() \n
		Selects, if the roll mode is started automatically by the instrument or if it is turned off. \n
			:return: mode: No help available
		"""
		response = self._core.io.query_str('TIMebase:ROLL:ENABle?')
		return Conversions.str_to_scalar_enum(response, enums.TimebaseRollMode)

	def set_enable(self, mode: enums.TimebaseRollMode) -> None:
		"""TIMebase:ROLL:ENABle \n
		Snippet: driver.timebase.roll.set_enable(mode = enums.TimebaseRollMode.AUTO) \n
		Selects, if the roll mode is started automatically by the instrument or if it is turned off. \n
			:param mode: No help available
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.TimebaseRollMode)
		self._core.io.write(f'TIMebase:ROLL:ENABle {param}')

	def get_state(self) -> bool:
		"""TIMebase:ROLL:STATe \n
		Snippet: value: bool = driver.timebase.roll.get_state() \n
		Returns the status of the roll mode. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('TIMebase:ROLL:STATe?')
		return Conversions.str_to_bool(response)

	def get_mtime(self) -> float:
		"""TIMebase:ROLL:MTIMe \n
		Snippet: value: float = driver.timebase.roll.get_mtime() \n
		Sets the minimum acquisition time for the automatic start of the roll mode. \n
			:return: min_time_fr_roll_md: No help available
		"""
		response = self._core.io.query_str('TIMebase:ROLL:MTIMe?')
		return Conversions.str_to_float(response)

	def set_mtime(self, min_time_fr_roll_md: float) -> None:
		"""TIMebase:ROLL:MTIMe \n
		Snippet: driver.timebase.roll.set_mtime(min_time_fr_roll_md = 1.0) \n
		Sets the minimum acquisition time for the automatic start of the roll mode. \n
			:param min_time_fr_roll_md: No help available
		"""
		param = Conversions.decimal_value_to_str(min_time_fr_roll_md)
		self._core.io.write(f'TIMebase:ROLL:MTIMe {param}')
