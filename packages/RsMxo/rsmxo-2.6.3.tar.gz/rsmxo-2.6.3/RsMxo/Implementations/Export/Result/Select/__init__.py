from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SelectCls:
	"""Select commands group definition. 6 total commands, 2 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("select", core, parent)

	@property
	def fra(self):
		"""fra commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_fra'):
			from .Fra import FraCls
			self._fra = FraCls(self._core, self._cmd_group)
		return self._fra

	@property
	def power(self):
		"""power commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_power'):
			from .Power import PowerCls
			self._power = PowerCls(self._core, self._cmd_group)
		return self._power

	def get_cursor(self) -> bool:
		"""EXPort:RESult:SELect:CURSor \n
		Snippet: value: bool = driver.export.result.select.get_cursor() \n
		Includes the current cursor results in the export file. \n
			:return: cursor_result: No help available
		"""
		response = self._core.io.query_str('EXPort:RESult:SELect:CURSor?')
		return Conversions.str_to_bool(response)

	def set_cursor(self, cursor_result: bool) -> None:
		"""EXPort:RESult:SELect:CURSor \n
		Snippet: driver.export.result.select.set_cursor(cursor_result = False) \n
		Includes the current cursor results in the export file. \n
			:param cursor_result: No help available
		"""
		param = Conversions.bool_to_str(cursor_result)
		self._core.io.write(f'EXPort:RESult:SELect:CURSor {param}')

	def get_measurement(self) -> bool:
		"""EXPort:RESult:SELect:MEASurement \n
		Snippet: value: bool = driver.export.result.select.get_measurement() \n
		Includes the current automatic measurement results in the export file. \n
			:return: meas_result: No help available
		"""
		response = self._core.io.query_str('EXPort:RESult:SELect:MEASurement?')
		return Conversions.str_to_bool(response)

	def set_measurement(self, meas_result: bool) -> None:
		"""EXPort:RESult:SELect:MEASurement \n
		Snippet: driver.export.result.select.set_measurement(meas_result = False) \n
		Includes the current automatic measurement results in the export file. \n
			:param meas_result: No help available
		"""
		param = Conversions.bool_to_str(meas_result)
		self._core.io.write(f'EXPort:RESult:SELect:MEASurement {param}')

	def clone(self) -> 'SelectCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SelectCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
