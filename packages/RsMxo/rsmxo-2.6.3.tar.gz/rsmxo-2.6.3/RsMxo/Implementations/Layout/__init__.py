from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LayoutCls:
	"""Layout commands group definition. 45 total commands, 10 Subgroups, 0 group commands
	Repeated Capability: Layout, default value after init: Layout.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("layout", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_layout_get', 'repcap_layout_set', repcap.Layout.Nr1)

	def repcap_layout_set(self, layout: repcap.Layout) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Layout.Default.
		Default value after init: Layout.Nr1"""
		self._cmd_group.set_repcap_enum_value(layout)

	def repcap_layout_get(self) -> repcap.Layout:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def diagram(self):
		"""diagram commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_diagram'):
			from .Diagram import DiagramCls
			self._diagram = DiagramCls(self._core, self._cmd_group)
		return self._diagram

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
	def label(self):
		"""label commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_label'):
			from .Label import LabelCls
			self._label = LabelCls(self._core, self._cmd_group)
		return self._label

	@property
	def rposition(self):
		"""rposition commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rposition'):
			from .Rposition import RpositionCls
			self._rposition = RpositionCls(self._core, self._cmd_group)
		return self._rposition

	@property
	def active(self):
		"""active commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_active'):
			from .Active import ActiveCls
			self._active = ActiveCls(self._core, self._cmd_group)
		return self._active

	@property
	def sactive(self):
		"""sactive commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sactive'):
			from .Sactive import SactiveCls
			self._sactive = SactiveCls(self._core, self._cmd_group)
		return self._sactive

	@property
	def result(self):
		"""result commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def node(self):
		"""node commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_node'):
			from .Node import NodeCls
			self._node = NodeCls(self._core, self._cmd_group)
		return self._node

	@property
	def zoom(self):
		"""zoom commands group. 7 Sub-classes, 0 commands."""
		if not hasattr(self, '_zoom'):
			from .Zoom import ZoomCls
			self._zoom = ZoomCls(self._core, self._cmd_group)
		return self._zoom

	def clone(self) -> 'LayoutCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = LayoutCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
