from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GateCls:
	"""Gate commands group definition. 10 total commands, 8 Subgroups, 0 group commands
	Repeated Capability: Gate, default value after init: Gate.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gate", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_gate_get', 'repcap_gate_set', repcap.Gate.Nr1)

	def repcap_gate_set(self, gate: repcap.Gate) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Gate.Default.
		Default value after init: Gate.Nr1"""
		self._cmd_group.set_repcap_enum_value(gate)

	def repcap_gate_get(self) -> repcap.Gate:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def mode(self):
		"""mode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import ModeCls
			self._mode = ModeCls(self._core, self._cmd_group)
		return self._mode

	@property
	def show(self):
		"""show commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_show'):
			from .Show import ShowCls
			self._show = ShowCls(self._core, self._cmd_group)
		return self._show

	@property
	def zdiagram(self):
		"""zdiagram commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_zdiagram'):
			from .Zdiagram import ZdiagramCls
			self._zdiagram = ZdiagramCls(self._core, self._cmd_group)
		return self._zdiagram

	@property
	def cursor(self):
		"""cursor commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_cursor'):
			from .Cursor import CursorCls
			self._cursor = CursorCls(self._core, self._cmd_group)
		return self._cursor

	@property
	def gcoupling(self):
		"""gcoupling commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_gcoupling'):
			from .Gcoupling import GcouplingCls
			self._gcoupling = GcouplingCls(self._core, self._cmd_group)
		return self._gcoupling

	@property
	def absolute(self):
		"""absolute commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_absolute'):
			from .Absolute import AbsoluteCls
			self._absolute = AbsoluteCls(self._core, self._cmd_group)
		return self._absolute

	@property
	def relative(self):
		"""relative commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_relative'):
			from .Relative import RelativeCls
			self._relative = RelativeCls(self._core, self._cmd_group)
		return self._relative

	def clone(self) -> 'GateCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = GateCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
