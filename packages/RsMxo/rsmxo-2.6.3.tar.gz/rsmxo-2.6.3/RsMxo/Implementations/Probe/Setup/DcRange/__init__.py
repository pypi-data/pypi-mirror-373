from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DcRangeCls:
	"""DcRange commands group definition. 2 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dcRange", core, parent)

	@property
	def max(self):
		"""max commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_max'):
			from .Max import MaxCls
			self._max = MaxCls(self._core, self._cmd_group)
		return self._max

	@property
	def min(self):
		"""min commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_min'):
			from .Min import MinCls
			self._min = MinCls(self._core, self._cmd_group)
		return self._min

	def clone(self) -> 'DcRangeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DcRangeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
