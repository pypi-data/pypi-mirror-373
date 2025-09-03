from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RefLevelCls:
	"""RefLevel commands group definition. 12 total commands, 5 Subgroups, 0 group commands
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
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def lmode(self):
		"""lmode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_lmode'):
			from .Lmode import LmodeCls
			self._lmode = LmodeCls(self._core, self._cmd_group)
		return self._lmode

	@property
	def usrLevel(self):
		"""usrLevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_usrLevel'):
			from .UsrLevel import UsrLevelCls
			self._usrLevel = UsrLevelCls(self._core, self._cmd_group)
		return self._usrLevel

	@property
	def absolute(self):
		"""absolute commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_absolute'):
			from .Absolute import AbsoluteCls
			self._absolute = AbsoluteCls(self._core, self._cmd_group)
		return self._absolute

	@property
	def relative(self):
		"""relative commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_relative'):
			from .Relative import RelativeCls
			self._relative = RelativeCls(self._core, self._cmd_group)
		return self._relative

	def clone(self) -> 'RefLevelCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = RefLevelCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
