from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BurstCls:
	"""Burst commands group definition. 5 total commands, 5 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("burst", core, parent)

	@property
	def cycleCount(self):
		"""cycleCount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_cycleCount'):
			from .CycleCount import CycleCountCls
			self._cycleCount = CycleCountCls(self._core, self._cmd_group)
		return self._cycleCount

	@property
	def itime(self):
		"""itime commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_itime'):
			from .Itime import ItimeCls
			self._itime = ItimeCls(self._core, self._cmd_group)
		return self._itime

	@property
	def mode(self):
		"""mode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import ModeCls
			self._mode = ModeCls(self._core, self._cmd_group)
		return self._mode

	@property
	def sphase(self):
		"""sphase commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sphase'):
			from .Sphase import SphaseCls
			self._sphase = SphaseCls(self._core, self._cmd_group)
		return self._sphase

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	def clone(self) -> 'BurstCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = BurstCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
