from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PllCls:
	"""Pll commands group definition. 3 total commands, 3 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pll", core, parent)

	@property
	def order(self):
		"""order commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_order'):
			from .Order import OrderCls
			self._order = OrderCls(self._core, self._cmd_group)
		return self._order

	@property
	def damping(self):
		"""damping commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_damping'):
			from .Damping import DampingCls
			self._damping = DampingCls(self._core, self._cmd_group)
		return self._damping

	@property
	def sync(self):
		"""sync commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sync'):
			from .Sync import SyncCls
			self._sync = SyncCls(self._core, self._cmd_group)
		return self._sync

	def clone(self) -> 'PllCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = PllCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
