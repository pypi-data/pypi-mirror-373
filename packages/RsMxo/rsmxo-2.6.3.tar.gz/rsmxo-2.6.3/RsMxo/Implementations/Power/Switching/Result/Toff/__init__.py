from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ToffCls:
	"""Toff commands group definition. 16 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("toff", core, parent)

	@property
	def energy(self):
		"""energy commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_energy'):
			from .Energy import EnergyCls
			self._energy = EnergyCls(self._core, self._cmd_group)
		return self._energy

	@property
	def power(self):
		"""power commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_power'):
			from .Power import PowerCls
			self._power = PowerCls(self._core, self._cmd_group)
		return self._power

	def clone(self) -> 'ToffCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ToffCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
