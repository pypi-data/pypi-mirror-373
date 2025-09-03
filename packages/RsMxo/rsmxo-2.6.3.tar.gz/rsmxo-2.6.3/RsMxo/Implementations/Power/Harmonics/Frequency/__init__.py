from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 3 total commands, 3 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	@property
	def en(self):
		"""en commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_en'):
			from .En import EnCls
			self._en = EnCls(self._core, self._cmd_group)
		return self._en

	@property
	def mil(self):
		"""mil commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mil'):
			from .Mil import MilCls
			self._mil = MilCls(self._core, self._cmd_group)
		return self._mil

	@property
	def rtca(self):
		"""rtca commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rtca'):
			from .Rtca import RtcaCls
			self._rtca = RtcaCls(self._core, self._cmd_group)
		return self._rtca

	def clone(self) -> 'FrequencyCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FrequencyCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
