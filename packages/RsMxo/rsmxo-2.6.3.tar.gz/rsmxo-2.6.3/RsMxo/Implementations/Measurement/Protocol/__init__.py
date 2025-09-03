from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ProtocolCls:
	"""Protocol commands group definition. 6 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("protocol", core, parent)

	@property
	def fname(self):
		"""fname commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fname'):
			from .Fname import FnameCls
			self._fname = FnameCls(self._core, self._cmd_group)
		return self._fname

	@property
	def f2Name(self):
		"""f2Name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_f2Name'):
			from .F2Name import F2NameCls
			self._f2Name = F2NameCls(self._core, self._cmd_group)
		return self._f2Name

	@property
	def fdName(self):
		"""fdName commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fdName'):
			from .FdName import FdNameCls
			self._fdName = FdNameCls(self._core, self._cmd_group)
		return self._fdName

	@property
	def fd2Name(self):
		"""fd2Name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fd2Name'):
			from .Fd2Name import Fd2NameCls
			self._fd2Name = Fd2NameCls(self._core, self._cmd_group)
		return self._fd2Name

	@property
	def fdValue(self):
		"""fdValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fdValue'):
			from .FdValue import FdValueCls
			self._fdValue = FdValueCls(self._core, self._cmd_group)
		return self._fdValue

	@property
	def fd2Value(self):
		"""fd2Value commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fd2Value'):
			from .Fd2Value import Fd2ValueCls
			self._fd2Value = Fd2ValueCls(self._core, self._cmd_group)
		return self._fd2Value

	def clone(self) -> 'ProtocolCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ProtocolCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
