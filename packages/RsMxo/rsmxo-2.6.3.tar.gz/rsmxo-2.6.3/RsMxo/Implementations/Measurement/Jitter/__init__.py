from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class JitterCls:
	"""Jitter commands group definition. 7 total commands, 7 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("jitter", core, parent)

	@property
	def slope(self):
		"""slope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_slope'):
			from .Slope import SlopeCls
			self._slope = SlopeCls(self._core, self._cmd_group)
		return self._slope

	@property
	def ncycles(self):
		"""ncycles commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ncycles'):
			from .Ncycles import NcyclesCls
			self._ncycles = NcyclesCls(self._core, self._cmd_group)
		return self._ncycles

	@property
	def polarity(self):
		"""polarity commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_polarity'):
			from .Polarity import PolarityCls
			self._polarity = PolarityCls(self._core, self._cmd_group)
		return self._polarity

	@property
	def refLevel(self):
		"""refLevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_refLevel'):
			from .RefLevel import RefLevelCls
			self._refLevel = RefLevelCls(self._core, self._cmd_group)
		return self._refLevel

	@property
	def relPolarity(self):
		"""relPolarity commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_relPolarity'):
			from .RelPolarity import RelPolarityCls
			self._relPolarity = RelPolarityCls(self._core, self._cmd_group)
		return self._relPolarity

	@property
	def unit(self):
		"""unit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_unit'):
			from .Unit import UnitCls
			self._unit = UnitCls(self._core, self._cmd_group)
		return self._unit

	@property
	def tref(self):
		"""tref commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_tref'):
			from .Tref import TrefCls
			self._tref = TrefCls(self._core, self._cmd_group)
		return self._tref

	def clone(self) -> 'JitterCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = JitterCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
