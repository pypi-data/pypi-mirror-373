from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DisplayCls:
	"""Display commands group definition. 2 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("display", core, parent)

	@property
	def shbu(self):
		"""shbu commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_shbu'):
			from .Shbu import ShbuCls
			self._shbu = ShbuCls(self._core, self._cmd_group)
		return self._shbu

	@property
	def shdi(self):
		"""shdi commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_shdi'):
			from .Shdi import ShdiCls
			self._shdi = ShdiCls(self._core, self._cmd_group)
		return self._shdi

	def clone(self) -> 'DisplayCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DisplayCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
