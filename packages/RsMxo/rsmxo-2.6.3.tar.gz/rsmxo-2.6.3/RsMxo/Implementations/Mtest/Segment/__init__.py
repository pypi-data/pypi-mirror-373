from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SegmentCls:
	"""Segment commands group definition. 10 total commands, 5 Subgroups, 0 group commands
	Repeated Capability: Segment, default value after init: Segment.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("segment", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_segment_get', 'repcap_segment_set', repcap.Segment.Nr1)

	def repcap_segment_set(self, segment: repcap.Segment) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Segment.Default.
		Default value after init: Segment.Nr1"""
		self._cmd_group.set_repcap_enum_value(segment)

	def repcap_segment_get(self) -> repcap.Segment:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import AddCls
			self._add = AddCls(self._core, self._cmd_group)
		return self._add

	@property
	def remove(self):
		"""remove commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_remove'):
			from .Remove import RemoveCls
			self._remove = RemoveCls(self._core, self._cmd_group)
		return self._remove

	@property
	def count(self):
		"""count commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_count'):
			from .Count import CountCls
			self._count = CountCls(self._core, self._cmd_group)
		return self._count

	@property
	def valid(self):
		"""valid commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_valid'):
			from .Valid import ValidCls
			self._valid = ValidCls(self._core, self._cmd_group)
		return self._valid

	@property
	def point(self):
		"""point commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_point'):
			from .Point import PointCls
			self._point = PointCls(self._core, self._cmd_group)
		return self._point

	def clone(self) -> 'SegmentCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SegmentCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
