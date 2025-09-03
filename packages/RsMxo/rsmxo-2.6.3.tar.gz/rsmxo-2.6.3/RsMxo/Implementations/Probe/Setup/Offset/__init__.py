from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OffsetCls:
	"""Offset commands group definition. 6 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	@property
	def azero(self):
		"""azero commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_azero'):
			from .Azero import AzeroCls
			self._azero = AzeroCls(self._core, self._cmd_group)
		return self._azero

	@property
	def useAutoZero(self):
		"""useAutoZero commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_useAutoZero'):
			from .UseAutoZero import UseAutoZeroCls
			self._useAutoZero = UseAutoZeroCls(self._core, self._cmd_group)
		return self._useAutoZero

	@property
	def stProbe(self):
		"""stProbe commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stProbe'):
			from .StProbe import StProbeCls
			self._stProbe = StProbeCls(self._core, self._cmd_group)
		return self._stProbe

	@property
	def zadjust(self):
		"""zadjust commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_zadjust'):
			from .Zadjust import ZadjustCls
			self._zadjust = ZadjustCls(self._core, self._cmd_group)
		return self._zadjust

	@property
	def toMean(self):
		"""toMean commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_toMean'):
			from .ToMean import ToMeanCls
			self._toMean = ToMeanCls(self._core, self._cmd_group)
		return self._toMean

	@property
	def topMeter(self):
		"""topMeter commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_topMeter'):
			from .TopMeter import TopMeterCls
			self._topMeter = TopMeterCls(self._core, self._cmd_group)
		return self._topMeter

	def clone(self) -> 'OffsetCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = OffsetCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
