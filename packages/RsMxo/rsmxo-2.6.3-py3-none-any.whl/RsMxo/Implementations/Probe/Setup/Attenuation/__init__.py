from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AttenuationCls:
	"""Attenuation commands group definition. 6 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("attenuation", core, parent)

	@property
	def auto(self):
		"""auto commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_auto'):
			from .Auto import AutoCls
			self._auto = AutoCls(self._core, self._cmd_group)
		return self._auto

	@property
	def manual(self):
		"""manual commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_manual'):
			from .Manual import ManualCls
			self._manual = ManualCls(self._core, self._cmd_group)
		return self._manual

	@property
	def mode(self):
		"""mode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import ModeCls
			self._mode = ModeCls(self._core, self._cmd_group)
		return self._mode

	@property
	def unit(self):
		"""unit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_unit'):
			from .Unit import UnitCls
			self._unit = UnitCls(self._core, self._cmd_group)
		return self._unit

	@property
	def defProbe(self):
		"""defProbe commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_defProbe'):
			from .DefProbe import DefProbeCls
			self._defProbe = DefProbeCls(self._core, self._cmd_group)
		return self._defProbe

	@property
	def tdefProbe(self):
		"""tdefProbe commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_tdefProbe'):
			from .TdefProbe import TdefProbeCls
			self._tdefProbe = TdefProbeCls(self._core, self._cmd_group)
		return self._tdefProbe

	def clone(self) -> 'AttenuationCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AttenuationCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
