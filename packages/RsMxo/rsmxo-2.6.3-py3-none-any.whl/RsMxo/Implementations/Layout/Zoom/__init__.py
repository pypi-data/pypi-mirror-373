from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ZoomCls:
	"""Zoom commands group definition. 27 total commands, 7 Subgroups, 0 group commands
	Repeated Capability: Zoom, default value after init: Zoom.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zoom", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_zoom_get', 'repcap_zoom_set', repcap.Zoom.Nr1)

	def repcap_zoom_set(self, zoom: repcap.Zoom) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Zoom.Default.
		Default value after init: Zoom.Nr1"""
		self._cmd_group.set_repcap_enum_value(zoom)

	def repcap_zoom_get(self) -> repcap.Zoom:
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
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def diagnostic(self):
		"""diagnostic commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_diagnostic'):
			from .Diagnostic import DiagnosticCls
			self._diagnostic = DiagnosticCls(self._core, self._cmd_group)
		return self._diagnostic

	@property
	def sscreen(self):
		"""sscreen commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sscreen'):
			from .Sscreen import SscreenCls
			self._sscreen = SscreenCls(self._core, self._cmd_group)
		return self._sscreen

	@property
	def horizontal(self):
		"""horizontal commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_horizontal'):
			from .Horizontal import HorizontalCls
			self._horizontal = HorizontalCls(self._core, self._cmd_group)
		return self._horizontal

	@property
	def vertical(self):
		"""vertical commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_vertical'):
			from .Vertical import VerticalCls
			self._vertical = VerticalCls(self._core, self._cmd_group)
		return self._vertical

	def clone(self) -> 'ZoomCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ZoomCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
