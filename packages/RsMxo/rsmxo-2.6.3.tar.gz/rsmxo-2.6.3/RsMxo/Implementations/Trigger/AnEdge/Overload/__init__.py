from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OverloadCls:
	"""Overload commands group definition. 5 total commands, 1 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("overload", core, parent)

	@property
	def status(self):
		"""status commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_status'):
			from .Status import StatusCls
			self._status = StatusCls(self._core, self._cmd_group)
		return self._status

	def clone(self) -> 'OverloadCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = OverloadCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
