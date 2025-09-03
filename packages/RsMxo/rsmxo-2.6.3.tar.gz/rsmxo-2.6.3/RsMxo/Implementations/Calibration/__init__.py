from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CalibrationCls:
	"""Calibration commands group definition. 4 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("calibration", core, parent)

	@property
	def all(self):
		"""all commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_all'):
			from .All import AllCls
			self._all = AllCls(self._core, self._cmd_group)
		return self._all

	# noinspection PyTypeChecker
	def get_result(self) -> enums.ResultState:
		"""CALibration:RESult \n
		Snippet: value: enums.ResultState = driver.calibration.get_result() \n
		Returns the result of the last self-alignment and the current alignment status. In remote mode, *CAL? provides more
		detailed information. \n
			:return: result_state: No help available
		"""
		response = self._core.io.query_str('CALibration:RESult?')
		return Conversions.str_to_scalar_enum(response, enums.ResultState)

	def get_date(self) -> str:
		"""CALibration:DATE \n
		Snippet: value: str = driver.calibration.get_date() \n
		Returns the date of the last self-alignment. \n
			:return: date: No help available
		"""
		response = self._core.io.query_str('CALibration:DATE?')
		return trim_str_response(response)

	def get_time(self) -> str:
		"""CALibration:TIME \n
		Snippet: value: str = driver.calibration.get_time() \n
		Returns the time of the last self-alignment. \n
			:return: time: No help available
		"""
		response = self._core.io.query_str('CALibration:TIME?')
		return trim_str_response(response)

	def clone(self) -> 'CalibrationCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CalibrationCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
