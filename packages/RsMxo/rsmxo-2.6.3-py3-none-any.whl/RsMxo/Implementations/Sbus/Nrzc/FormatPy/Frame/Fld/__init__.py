from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.RepeatedCapability import RepeatedCapability
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FldCls:
	"""Fld commands group definition. 7 total commands, 7 Subgroups, 0 group commands
	Repeated Capability: Field, default value after init: Field.Ix1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fld", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_field_get', 'repcap_field_set', repcap.Field.Ix1)

	def repcap_field_set(self, field: repcap.Field) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Field.Default.
		Default value after init: Field.Ix1"""
		self._cmd_group.set_repcap_enum_value(field)

	def repcap_field_get(self) -> repcap.Field:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	@property
	def bitcount(self):
		"""bitcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bitcount'):
			from .Bitcount import BitcountCls
			self._bitcount = BitcountCls(self._core, self._cmd_group)
		return self._bitcount

	@property
	def condition(self):
		"""condition commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_condition'):
			from .Condition import ConditionCls
			self._condition = ConditionCls(self._core, self._cmd_group)
		return self._condition

	@property
	def formatPy(self):
		"""formatPy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_formatPy'):
			from .FormatPy import FormatPyCls
			self._formatPy = FormatPyCls(self._core, self._cmd_group)
		return self._formatPy

	@property
	def bitOrder(self):
		"""bitOrder commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bitOrder'):
			from .BitOrder import BitOrderCls
			self._bitOrder = BitOrderCls(self._core, self._cmd_group)
		return self._bitOrder

	@property
	def color(self):
		"""color commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_color'):
			from .Color import ColorCls
			self._color = ColorCls(self._core, self._cmd_group)
		return self._color

	@property
	def clmn(self):
		"""clmn commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clmn'):
			from .Clmn import ClmnCls
			self._clmn = ClmnCls(self._core, self._cmd_group)
		return self._clmn

	def clone(self) -> 'FldCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FldCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
