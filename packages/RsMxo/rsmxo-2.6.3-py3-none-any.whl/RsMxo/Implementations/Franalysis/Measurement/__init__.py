from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MeasurementCls:
	"""Measurement commands group definition. 6 total commands, 2 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("measurement", core, parent)

	@property
	def delay(self):
		"""delay commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_delay'):
			from .Delay import DelayCls
			self._delay = DelayCls(self._core, self._cmd_group)
		return self._delay

	@property
	def point(self):
		"""point commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_point'):
			from .Point import PointCls
			self._point = PointCls(self._core, self._cmd_group)
		return self._point

	# noinspection PyTypeChecker
	def get_rbw(self) -> enums.MeasRbw:
		"""FRANalysis:MEASurement:RBW \n
		Snippet: value: enums.MeasRbw = driver.franalysis.measurement.get_rbw() \n
		Sets the resolution bandwidth, which determines the number of measurements that are used for creating the plot. \n
			:return: rbw: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MEASurement:RBW?')
		return Conversions.str_to_scalar_enum(response, enums.MeasRbw)

	def set_rbw(self, rbw: enums.MeasRbw) -> None:
		"""FRANalysis:MEASurement:RBW \n
		Snippet: driver.franalysis.measurement.set_rbw(rbw = enums.MeasRbw.HIGH) \n
		Sets the resolution bandwidth, which determines the number of measurements that are used for creating the plot. \n
			:param rbw: No help available
		"""
		param = Conversions.enum_scalar_to_str(rbw, enums.MeasRbw)
		self._core.io.write(f'FRANalysis:MEASurement:RBW {param}')

	def clone(self) -> 'MeasurementCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MeasurementCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
