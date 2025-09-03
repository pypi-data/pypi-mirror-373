from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LevelCls:
	"""Level commands group definition. 7 total commands, 4 Subgroups, 0 group commands
	Repeated Capability: Lvl, default value after init: Lvl.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("level", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_lvl_get', 'repcap_lvl_set', repcap.Lvl.Nr1)

	def repcap_lvl_set(self, lvl: repcap.Lvl) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Lvl.Default.
		Default value after init: Lvl.Nr1"""
		self._cmd_group.set_repcap_enum_value(lvl)

	def repcap_lvl_get(self) -> repcap.Lvl:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def value(self):
		"""value commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_value'):
			from .Value import ValueCls
			self._value = ValueCls(self._core, self._cmd_group)
		return self._value

	@property
	def runt(self):
		"""runt commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_runt'):
			from .Runt import RuntCls
			self._runt = RuntCls(self._core, self._cmd_group)
		return self._runt

	@property
	def slew(self):
		"""slew commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_slew'):
			from .Slew import SlewCls
			self._slew = SlewCls(self._core, self._cmd_group)
		return self._slew

	@property
	def window(self):
		"""window commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_window'):
			from .Window import WindowCls
			self._window = WindowCls(self._core, self._cmd_group)
		return self._window

	def clone(self) -> 'LevelCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = LevelCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
