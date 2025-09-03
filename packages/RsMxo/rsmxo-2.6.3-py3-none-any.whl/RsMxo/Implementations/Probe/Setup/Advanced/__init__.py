from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AdvancedCls:
	"""Advanced commands group definition. 6 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("advanced", core, parent)

	@property
	def audioverload(self):
		"""audioverload commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_audioverload'):
			from .Audioverload import AudioverloadCls
			self._audioverload = AudioverloadCls(self._core, self._cmd_group)
		return self._audioverload

	@property
	def filterPy(self):
		"""filterPy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_filterPy'):
			from .FilterPy import FilterPyCls
			self._filterPy = FilterPyCls(self._core, self._cmd_group)
		return self._filterPy

	@property
	def range(self):
		"""range commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_range'):
			from .Range import RangeCls
			self._range = RangeCls(self._core, self._cmd_group)
		return self._range

	@property
	def pmtOffset(self):
		"""pmtOffset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pmtOffset'):
			from .PmtOffset import PmtOffsetCls
			self._pmtOffset = PmtOffsetCls(self._core, self._cmd_group)
		return self._pmtOffset

	@property
	def unit(self):
		"""unit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_unit'):
			from .Unit import UnitCls
			self._unit = UnitCls(self._core, self._cmd_group)
		return self._unit

	@property
	def rdefaults(self):
		"""rdefaults commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rdefaults'):
			from .Rdefaults import RdefaultsCls
			self._rdefaults = RdefaultsCls(self._core, self._cmd_group)
		return self._rdefaults

	def clone(self) -> 'AdvancedCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AdvancedCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
