from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DisplayCls:
	"""Display commands group definition. 12 total commands, 8 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("display", core, parent)

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def label(self):
		"""label commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_label'):
			from .Label import LabelCls
			self._label = LabelCls(self._core, self._cmd_group)
		return self._label

	@property
	def power(self):
		"""power commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_power'):
			from .Power import PowerCls
			self._power = PowerCls(self._core, self._cmd_group)
		return self._power

	@property
	def conduction(self):
		"""conduction commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_conduction'):
			from .Conduction import ConductionCls
			self._conduction = ConductionCls(self._core, self._cmd_group)
		return self._conduction

	@property
	def nconduction(self):
		"""nconduction commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_nconduction'):
			from .Nconduction import NconductionCls
			self._nconduction = NconductionCls(self._core, self._cmd_group)
		return self._nconduction

	@property
	def toff(self):
		"""toff commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_toff'):
			from .Toff import ToffCls
			self._toff = ToffCls(self._core, self._cmd_group)
		return self._toff

	@property
	def ton(self):
		"""ton commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_ton'):
			from .Ton import TonCls
			self._ton = TonCls(self._core, self._cmd_group)
		return self._ton

	@property
	def total(self):
		"""total commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_total'):
			from .Total import TotalCls
			self._total = TotalCls(self._core, self._cmd_group)
		return self._total

	def clone(self) -> 'DisplayCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DisplayCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
