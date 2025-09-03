from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VoltageCls:
	"""Voltage commands group definition. 32 total commands, 4 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("voltage", core, parent)

	@property
	def rms(self):
		"""rms commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_rms'):
			from .Rms import RmsCls
			self._rms = RmsCls(self._core, self._cmd_group)
		return self._rms

	@property
	def frequency(self):
		"""frequency commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def crestFactor(self):
		"""crestFactor commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_crestFactor'):
			from .CrestFactor import CrestFactorCls
			self._crestFactor = CrestFactorCls(self._core, self._cmd_group)
		return self._crestFactor

	@property
	def peak(self):
		"""peak commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_peak'):
			from .Peak import PeakCls
			self._peak = PeakCls(self._core, self._cmd_group)
		return self._peak

	def clone(self) -> 'VoltageCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = VoltageCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
