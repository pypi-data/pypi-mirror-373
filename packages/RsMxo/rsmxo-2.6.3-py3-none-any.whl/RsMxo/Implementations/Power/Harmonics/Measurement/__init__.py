from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MeasurementCls:
	"""Measurement commands group definition. 4 total commands, 4 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("measurement", core, parent)

	@property
	def frequency(self):
		"""frequency commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def realPower(self):
		"""realPower commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_realPower'):
			from .RealPower import RealPowerCls
			self._realPower = RealPowerCls(self._core, self._cmd_group)
		return self._realPower

	@property
	def thdFundament(self):
		"""thdFundament commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_thdFundament'):
			from .ThdFundament import ThdFundamentCls
			self._thdFundament = ThdFundamentCls(self._core, self._cmd_group)
		return self._thdFundament

	@property
	def thdRms(self):
		"""thdRms commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_thdRms'):
			from .ThdRms import ThdRmsCls
			self._thdRms = ThdRmsCls(self._core, self._cmd_group)
		return self._thdRms

	def clone(self) -> 'MeasurementCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MeasurementCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
