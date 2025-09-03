from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.RepeatedCapability import RepeatedCapability
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FldCls:
	"""Fld commands group definition. 5 total commands, 5 Subgroups, 0 group commands
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
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def bit(self):
		"""bit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bit'):
			from .Bit import BitCls
			self._bit = BitCls(self._core, self._cmd_group)
		return self._bit

	@property
	def doperator(self):
		"""doperator commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_doperator'):
			from .Doperator import DoperatorCls
			self._doperator = DoperatorCls(self._core, self._cmd_group)
		return self._doperator

	@property
	def dmin(self):
		"""dmin commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dmin'):
			from .Dmin import DminCls
			self._dmin = DminCls(self._core, self._cmd_group)
		return self._dmin

	@property
	def dmax(self):
		"""dmax commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dmax'):
			from .Dmax import DmaxCls
			self._dmax = DmaxCls(self._core, self._cmd_group)
		return self._dmax

	def clone(self) -> 'FldCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FldCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
