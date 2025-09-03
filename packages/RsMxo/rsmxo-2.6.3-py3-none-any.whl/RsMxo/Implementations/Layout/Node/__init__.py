from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NodeCls:
	"""Node commands group definition. 6 total commands, 5 Subgroups, 0 group commands
	Repeated Capability: NodeIx, default value after init: NodeIx.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("node", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_nodeIx_get', 'repcap_nodeIx_set', repcap.NodeIx.Nr1)

	def repcap_nodeIx_set(self, nodeIx: repcap.NodeIx) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to NodeIx.Default.
		Default value after init: NodeIx.Nr1"""
		self._cmd_group.set_repcap_enum_value(nodeIx)

	def repcap_nodeIx_get(self) -> repcap.NodeIx:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def count(self):
		"""count commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_count'):
			from .Count import CountCls
			self._count = CountCls(self._core, self._cmd_group)
		return self._count

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def stype(self):
		"""stype commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stype'):
			from .Stype import StypeCls
			self._stype = StypeCls(self._core, self._cmd_group)
		return self._stype

	@property
	def ratio(self):
		"""ratio commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ratio'):
			from .Ratio import RatioCls
			self._ratio = RatioCls(self._core, self._cmd_group)
		return self._ratio

	@property
	def children(self):
		"""children commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_children'):
			from .Children import ChildrenCls
			self._children = ChildrenCls(self._core, self._cmd_group)
		return self._children

	def clone(self) -> 'NodeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = NodeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
