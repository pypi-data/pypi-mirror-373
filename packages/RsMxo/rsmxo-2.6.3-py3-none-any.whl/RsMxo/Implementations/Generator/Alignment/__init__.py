from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AlignmentCls:
	"""Alignment commands group definition. 3 total commands, 1 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("alignment", core, parent)

	@property
	def dc(self):
		"""dc commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_dc'):
			from .Dc import DcCls
			self._dc = DcCls(self._core, self._cmd_group)
		return self._dc

	def clone(self) -> 'AlignmentCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AlignmentCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
