from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DvMeterCls:
	"""DvMeter commands group definition. 7 total commands, 4 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dvMeter", core, parent)

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def dc(self):
		"""dc commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_dc'):
			from .Dc import DcCls
			self._dc = DcCls(self._core, self._cmd_group)
		return self._dc

	@property
	def dcrms(self):
		"""dcrms commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_dcrms'):
			from .Dcrms import DcrmsCls
			self._dcrms = DcrmsCls(self._core, self._cmd_group)
		return self._dcrms

	@property
	def acRms(self):
		"""acRms commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_acRms'):
			from .AcRms import AcRmsCls
			self._acRms = AcRmsCls(self._core, self._cmd_group)
		return self._acRms

	def clone(self) -> 'DvMeterCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DvMeterCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
