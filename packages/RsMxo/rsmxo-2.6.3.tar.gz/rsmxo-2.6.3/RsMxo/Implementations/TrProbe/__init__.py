from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TrProbeCls:
	"""TrProbe commands group definition. 5 total commands, 1 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("trProbe", core, parent)

	@property
	def setup(self):
		"""setup commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_setup'):
			from .Setup import SetupCls
			self._setup = SetupCls(self._core, self._cmd_group)
		return self._setup

	def clone(self) -> 'TrProbeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = TrProbeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
