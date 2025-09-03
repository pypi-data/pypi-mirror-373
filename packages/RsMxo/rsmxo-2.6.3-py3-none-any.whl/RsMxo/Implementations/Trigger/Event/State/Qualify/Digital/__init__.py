from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DigitalCls:
	"""Digital commands group definition. 3 total commands, 3 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("digital", core, parent)

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def logic(self):
		"""logic commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_logic'):
			from .Logic import LogicCls
			self._logic = LogicCls(self._core, self._cmd_group)
		return self._logic

	@property
	def chan(self):
		"""chan commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_chan'):
			from .Chan import ChanCls
			self._chan = ChanCls(self._core, self._cmd_group)
		return self._chan

	def clone(self) -> 'DigitalCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DigitalCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
