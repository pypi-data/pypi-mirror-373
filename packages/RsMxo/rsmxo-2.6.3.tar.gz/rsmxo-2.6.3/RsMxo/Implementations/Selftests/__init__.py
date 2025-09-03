from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SelftestsCls:
	"""Selftests commands group definition. 2 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("selftests", core, parent)

	@property
	def runSelected(self):
		"""runSelected commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_runSelected'):
			from .RunSelected import RunSelectedCls
			self._runSelected = RunSelectedCls(self._core, self._cmd_group)
		return self._runSelected

	@property
	def available(self):
		"""available commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_available'):
			from .Available import AvailableCls
			self._available = AvailableCls(self._core, self._cmd_group)
		return self._available

	def clone(self) -> 'SelftestsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SelftestsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
