from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThresholdCls:
	"""Threshold commands group definition. 3 total commands, 3 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("threshold", core, parent)

	@property
	def high(self):
		"""high commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_high'):
			from .High import HighCls
			self._high = HighCls(self._core, self._cmd_group)
		return self._high

	@property
	def low(self):
		"""low commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_low'):
			from .Low import LowCls
			self._low = LowCls(self._core, self._cmd_group)
		return self._low

	@property
	def hysteresis(self):
		"""hysteresis commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_hysteresis'):
			from .Hysteresis import HysteresisCls
			self._hysteresis = HysteresisCls(self._core, self._cmd_group)
		return self._hysteresis

	def clone(self) -> 'ThresholdCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ThresholdCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
