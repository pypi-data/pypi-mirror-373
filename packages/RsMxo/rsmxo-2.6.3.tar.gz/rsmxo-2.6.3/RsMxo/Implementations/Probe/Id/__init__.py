from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IdCls:
	"""Id commands group definition. 4 total commands, 4 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("id", core, parent)

	@property
	def partNumber(self):
		"""partNumber commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_partNumber'):
			from .PartNumber import PartNumberCls
			self._partNumber = PartNumberCls(self._core, self._cmd_group)
		return self._partNumber

	@property
	def prDate(self):
		"""prDate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_prDate'):
			from .PrDate import PrDateCls
			self._prDate = PrDateCls(self._core, self._cmd_group)
		return self._prDate

	@property
	def srNumber(self):
		"""srNumber commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_srNumber'):
			from .SrNumber import SrNumberCls
			self._srNumber = SrNumberCls(self._core, self._cmd_group)
		return self._srNumber

	@property
	def swVersion(self):
		"""swVersion commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_swVersion'):
			from .SwVersion import SwVersionCls
			self._swVersion = SwVersionCls(self._core, self._cmd_group)
		return self._swVersion

	def clone(self) -> 'IdCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = IdCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
