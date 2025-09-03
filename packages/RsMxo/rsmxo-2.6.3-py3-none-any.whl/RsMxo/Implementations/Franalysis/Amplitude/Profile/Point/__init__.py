from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.RepeatedCapability import RepeatedCapability
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PointCls:
	"""Point commands group definition. 3 total commands, 3 Subgroups, 0 group commands
	Repeated Capability: Point, default value after init: Point.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("point", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_point_get', 'repcap_point_set', repcap.Point.Nr1)

	def repcap_point_set(self, point: repcap.Point) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Point.Default.
		Default value after init: Point.Nr1"""
		self._cmd_group.set_repcap_enum_value(point)

	def repcap_point_get(self) -> repcap.Point:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def amplitude(self):
		"""amplitude commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_amplitude'):
			from .Amplitude import AmplitudeCls
			self._amplitude = AmplitudeCls(self._core, self._cmd_group)
		return self._amplitude

	@property
	def frequency(self):
		"""frequency commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def remove(self):
		"""remove commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_remove'):
			from .Remove import RemoveCls
			self._remove = RemoveCls(self._core, self._cmd_group)
		return self._remove

	def clone(self) -> 'PointCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = PointCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
