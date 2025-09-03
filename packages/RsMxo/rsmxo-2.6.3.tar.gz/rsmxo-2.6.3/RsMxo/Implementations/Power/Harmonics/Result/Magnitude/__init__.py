from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MagnitudeCls:
	"""Magnitude commands group definition. 6 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("magnitude", core, parent)

	@property
	def rms(self):
		"""rms commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_rms'):
			from .Rms import RmsCls
			self._rms = RmsCls(self._core, self._cmd_group)
		return self._rms

	@property
	def percent(self):
		"""percent commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_percent'):
			from .Percent import PercentCls
			self._percent = PercentCls(self._core, self._cmd_group)
		return self._percent

	def clone(self) -> 'MagnitudeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MagnitudeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
