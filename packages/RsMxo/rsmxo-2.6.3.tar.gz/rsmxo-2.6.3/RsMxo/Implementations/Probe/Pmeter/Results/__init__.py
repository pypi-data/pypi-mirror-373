from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultsCls:
	"""Results commands group definition. 5 total commands, 5 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("results", core, parent)

	@property
	def common(self):
		"""common commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_common'):
			from .Common import CommonCls
			self._common = CommonCls(self._core, self._cmd_group)
		return self._common

	@property
	def differential(self):
		"""differential commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_differential'):
			from .Differential import DifferentialCls
			self._differential = DifferentialCls(self._core, self._cmd_group)
		return self._differential

	@property
	def positive(self):
		"""positive commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_positive'):
			from .Positive import PositiveCls
			self._positive = PositiveCls(self._core, self._cmd_group)
		return self._positive

	@property
	def negative(self):
		"""negative commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_negative'):
			from .Negative import NegativeCls
			self._negative = NegativeCls(self._core, self._cmd_group)
		return self._negative

	@property
	def single(self):
		"""single commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_single'):
			from .Single import SingleCls
			self._single = SingleCls(self._core, self._cmd_group)
		return self._single

	def clone(self) -> 'ResultsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ResultsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
