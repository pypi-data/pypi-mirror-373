from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal.RepeatedCapability import RepeatedCapability
from ........ import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LogicCls:
	"""Logic commands group definition. 3 total commands, 3 Subgroups, 0 group commands
	Repeated Capability: Logic, default value after init: Logic.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("logic", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_logic_get', 'repcap_logic_set', repcap.Logic.Nr1)

	def repcap_logic_set(self, logic: repcap.Logic) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Logic.Default.
		Default value after init: Logic.Nr1"""
		self._cmd_group.set_repcap_enum_value(logic)

	def repcap_logic_get(self) -> repcap.Logic:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def ab(self):
		"""ab commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ab'):
			from .Ab import AbCls
			self._ab = AbCls(self._core, self._cmd_group)
		return self._ab

	@property
	def cd(self):
		"""cd commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_cd'):
			from .Cd import CdCls
			self._cd = CdCls(self._core, self._cmd_group)
		return self._cd

	@property
	def abcd(self):
		"""abcd commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_abcd'):
			from .Abcd import AbcdCls
			self._abcd = AbcdCls(self._core, self._cmd_group)
		return self._abcd

	def clone(self) -> 'LogicCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = LogicCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
