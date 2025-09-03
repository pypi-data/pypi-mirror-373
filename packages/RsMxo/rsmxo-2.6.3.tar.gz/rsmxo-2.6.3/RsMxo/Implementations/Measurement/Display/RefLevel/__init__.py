from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RefLevelCls:
	"""RefLevel commands group definition. 3 total commands, 3 Subgroups, 0 group commands
	Repeated Capability: RefLevel, default value after init: RefLevel.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("refLevel", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_refLevel_get', 'repcap_refLevel_set', repcap.RefLevel.Nr1)

	def repcap_refLevel_set(self, refLevel: repcap.RefLevel) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to RefLevel.Default.
		Default value after init: RefLevel.Nr1"""
		self._cmd_group.set_repcap_enum_value(refLevel)

	def repcap_refLevel_get(self) -> repcap.RefLevel:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def histogram(self):
		"""histogram commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_histogram'):
			from .Histogram import HistogramCls
			self._histogram = HistogramCls(self._core, self._cmd_group)
		return self._histogram

	@property
	def levels(self):
		"""levels commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_levels'):
			from .Levels import LevelsCls
			self._levels = LevelsCls(self._core, self._cmd_group)
		return self._levels

	@property
	def style(self):
		"""style commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_style'):
			from .Style import StyleCls
			self._style = StyleCls(self._core, self._cmd_group)
		return self._style

	def clone(self) -> 'RefLevelCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = RefLevelCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
