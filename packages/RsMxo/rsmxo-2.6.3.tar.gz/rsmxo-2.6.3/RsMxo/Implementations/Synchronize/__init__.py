from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SynchronizeCls:
	"""Synchronize commands group definition. 14 total commands, 3 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("synchronize", core, parent)

	@property
	def disconnect(self):
		"""disconnect commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_disconnect'):
			from .Disconnect import DisconnectCls
			self._disconnect = DisconnectCls(self._core, self._cmd_group)
		return self._disconnect

	@property
	def device(self):
		"""device commands group. 9 Sub-classes, 0 commands."""
		if not hasattr(self, '_device'):
			from .Device import DeviceCls
			self._device = DeviceCls(self._core, self._cmd_group)
		return self._device

	@property
	def load(self):
		"""load commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_load'):
			from .Load import LoadCls
			self._load = LoadCls(self._core, self._cmd_group)
		return self._load

	def clone(self) -> 'SynchronizeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SynchronizeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
