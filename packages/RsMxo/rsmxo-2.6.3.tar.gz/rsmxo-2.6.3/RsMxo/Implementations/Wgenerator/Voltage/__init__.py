from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VoltageCls:
	"""Voltage commands group definition. 6 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("voltage", core, parent)

	@property
	def vpp(self):
		"""vpp commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_vpp'):
			from .Vpp import VppCls
			self._vpp = VppCls(self._core, self._cmd_group)
		return self._vpp

	@property
	def low(self):
		"""low commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_low'):
			from .Low import LowCls
			self._low = LowCls(self._core, self._cmd_group)
		return self._low

	@property
	def high(self):
		"""high commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_high'):
			from .High import HighCls
			self._high = HighCls(self._core, self._cmd_group)
		return self._high

	@property
	def offset(self):
		"""offset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_offset'):
			from .Offset import OffsetCls
			self._offset = OffsetCls(self._core, self._cmd_group)
		return self._offset

	@property
	def inversion(self):
		"""inversion commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_inversion'):
			from .Inversion import InversionCls
			self._inversion = InversionCls(self._core, self._cmd_group)
		return self._inversion

	@property
	def dcLevel(self):
		"""dcLevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dcLevel'):
			from .DcLevel import DcLevelCls
			self._dcLevel = DcLevelCls(self._core, self._cmd_group)
		return self._dcLevel

	def clone(self) -> 'VoltageCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = VoltageCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
