from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ZoneCls:
	"""Zone commands group definition. 20 total commands, 8 Subgroups, 0 group commands
	Repeated Capability: Zone, default value after init: Zone.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zone", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_zone_get', 'repcap_zone_set', repcap.Zone.Nr1)

	def repcap_zone_set(self, zone: repcap.Zone) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Zone.Default.
		Default value after init: Zone.Nr1"""
		self._cmd_group.set_repcap_enum_value(zone)

	def repcap_zone_get(self) -> repcap.Zone:
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
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def visible(self):
		"""visible commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_visible'):
			from .Visible import VisibleCls
			self._visible = VisibleCls(self._core, self._cmd_group)
		return self._visible

	@property
	def diagram(self):
		"""diagram commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_diagram'):
			from .Diagram import DiagramCls
			self._diagram = DiagramCls(self._core, self._cmd_group)
		return self._diagram

	@property
	def acombination(self):
		"""acombination commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_acombination'):
			from .Acombination import AcombinationCls
			self._acombination = AcombinationCls(self._core, self._cmd_group)
		return self._acombination

	@property
	def area(self):
		"""area commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_area'):
			from .Area import AreaCls
			self._area = AreaCls(self._core, self._cmd_group)
		return self._area

	def clone(self) -> 'ZoneCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ZoneCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
