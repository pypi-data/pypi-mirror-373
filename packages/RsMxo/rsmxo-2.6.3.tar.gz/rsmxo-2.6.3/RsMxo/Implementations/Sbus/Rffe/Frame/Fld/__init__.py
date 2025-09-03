from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.RepeatedCapability import RepeatedCapability
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FldCls:
	"""Fld commands group definition. 4 total commands, 4 Subgroups, 0 group commands
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
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	@property
	def fvalue(self):
		"""fvalue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fvalue'):
			from .Fvalue import FvalueCls
			self._fvalue = FvalueCls(self._core, self._cmd_group)
		return self._fvalue

	@property
	def value(self):
		"""value commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_value'):
			from .Value import ValueCls
			self._value = ValueCls(self._core, self._cmd_group)
		return self._value

	def clone(self) -> 'FldCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FldCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
