from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MtestCls:
	"""Mtest commands group definition. 31 total commands, 11 Subgroups, 0 group commands
	Repeated Capability: MaskTest, default value after init: MaskTest.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mtest", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_maskTest_get', 'repcap_maskTest_set', repcap.MaskTest.Nr1)

	def repcap_maskTest_set(self, maskTest: repcap.MaskTest) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to MaskTest.Default.
		Default value after init: MaskTest.Nr1"""
		self._cmd_group.set_repcap_enum_value(maskTest)

	def repcap_maskTest_get(self) -> repcap.MaskTest:
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
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

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
	def segment(self):
		"""segment commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_segment'):
			from .Segment import SegmentCls
			self._segment = SegmentCls(self._core, self._cmd_group)
		return self._segment

	@property
	def onViolation(self):
		"""onViolation commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_onViolation'):
			from .OnViolation import OnViolationCls
			self._onViolation = OnViolationCls(self._core, self._cmd_group)
		return self._onViolation

	@property
	def result(self):
		"""result commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def imExport(self):
		"""imExport commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_imExport'):
			from .ImExport import ImExportCls
			self._imExport = ImExportCls(self._core, self._cmd_group)
		return self._imExport

	def clone(self) -> 'MtestCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MtestCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
