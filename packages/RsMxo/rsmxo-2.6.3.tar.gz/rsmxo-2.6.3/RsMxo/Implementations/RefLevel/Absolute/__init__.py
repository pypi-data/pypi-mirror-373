from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AbsoluteCls:
	"""Absolute commands group definition. 4 total commands, 4 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("absolute", core, parent)

	@property
	def llevel(self):
		"""llevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_llevel'):
			from .Llevel import LlevelCls
			self._llevel = LlevelCls(self._core, self._cmd_group)
		return self._llevel

	@property
	def mlevel(self):
		"""mlevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mlevel'):
			from .Mlevel import MlevelCls
			self._mlevel = MlevelCls(self._core, self._cmd_group)
		return self._mlevel

	@property
	def ulevel(self):
		"""ulevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ulevel'):
			from .Ulevel import UlevelCls
			self._ulevel = UlevelCls(self._core, self._cmd_group)
		return self._ulevel

	@property
	def hysteresis(self):
		"""hysteresis commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_hysteresis'):
			from .Hysteresis import HysteresisCls
			self._hysteresis = HysteresisCls(self._core, self._cmd_group)
		return self._hysteresis

	def clone(self) -> 'AbsoluteCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AbsoluteCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
