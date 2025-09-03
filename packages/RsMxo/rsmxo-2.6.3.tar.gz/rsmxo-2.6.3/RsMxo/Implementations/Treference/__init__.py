from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TreferenceCls:
	"""Treference commands group definition. 20 total commands, 11 Subgroups, 0 group commands
	Repeated Capability: TimingReference, default value after init: TimingReference.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("treference", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_timingReference_get', 'repcap_timingReference_set', repcap.TimingReference.Nr1)

	def repcap_timingReference_set(self, timingReference: repcap.TimingReference) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to TimingReference.Default.
		Default value after init: TimingReference.Nr1"""
		self._cmd_group.set_repcap_enum_value(timingReference)

	def repcap_timingReference_get(self) -> repcap.TimingReference:
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
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def display(self):
		"""display commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def edge(self):
		"""edge commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_edge'):
			from .Edge import EdgeCls
			self._edge = EdgeCls(self._core, self._cmd_group)
		return self._edge

	@property
	def rflSet(self):
		"""rflSet commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rflSet'):
			from .RflSet import RflSetCls
			self._rflSet = RflSetCls(self._core, self._cmd_group)
		return self._rflSet

	@property
	def refLevel(self):
		"""refLevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_refLevel'):
			from .RefLevel import RefLevelCls
			self._refLevel = RefLevelCls(self._core, self._cmd_group)
		return self._refLevel

	@property
	def symRate(self):
		"""symRate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symRate'):
			from .SymRate import SymRateCls
			self._symRate = SymRateCls(self._core, self._cmd_group)
		return self._symRate

	@property
	def clk(self):
		"""clk commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_clk'):
			from .Clk import ClkCls
			self._clk = ClkCls(self._core, self._cmd_group)
		return self._clk

	@property
	def cdr(self):
		"""cdr commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_cdr'):
			from .Cdr import CdrCls
			self._cdr = CdrCls(self._core, self._cmd_group)
		return self._cdr

	def clone(self) -> 'TreferenceCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = TreferenceCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
