from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MaximumCls:
	"""Maximum commands group definition. 4 total commands, 4 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("maximum", core, parent)

	@property
	def left(self):
		"""left commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_left'):
			from .Left import LeftCls
			self._left = LeftCls(self._core, self._cmd_group)
		return self._left

	@property
	def next(self):
		"""next commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_next'):
			from .Next import NextCls
			self._next = NextCls(self._core, self._cmd_group)
		return self._next

	@property
	def peak(self):
		"""peak commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_peak'):
			from .Peak import PeakCls
			self._peak = PeakCls(self._core, self._cmd_group)
		return self._peak

	@property
	def right(self):
		"""right commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_right'):
			from .Right import RightCls
			self._right = RightCls(self._core, self._cmd_group)
		return self._right

	def clone(self) -> 'MaximumCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MaximumCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
