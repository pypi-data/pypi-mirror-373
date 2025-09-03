from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SetHoldCls:
	"""SetHold commands group definition. 5 total commands, 3 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("setHold", core, parent)

	@property
	def htime(self):
		"""htime commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_htime'):
			from .Htime import HtimeCls
			self._htime = HtimeCls(self._core, self._cmd_group)
		return self._htime

	@property
	def stime(self):
		"""stime commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stime'):
			from .Stime import StimeCls
			self._stime = StimeCls(self._core, self._cmd_group)
		return self._stime

	@property
	def csource(self):
		"""csource commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_csource'):
			from .Csource import CsourceCls
			self._csource = CsourceCls(self._core, self._cmd_group)
		return self._csource

	def clone(self) -> 'SetHoldCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SetHoldCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
