from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EventCls:
	"""Event commands group definition. 71 total commands, 14 Subgroups, 0 group commands
	Repeated Capability: Evnt, default value after init: Evnt.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("event", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_evnt_get', 'repcap_evnt_set', repcap.Evnt.Nr1)

	def repcap_evnt_set(self, evnt: repcap.Evnt) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Evnt.Default.
		Default value after init: Evnt.Nr1"""
		self._cmd_group.set_repcap_enum_value(evnt)

	def repcap_evnt_get(self) -> repcap.Evnt:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def level(self):
		"""level commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_level'):
			from .Level import LevelCls
			self._level = LevelCls(self._core, self._cmd_group)
		return self._level

	@property
	def setHold(self):
		"""setHold commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_setHold'):
			from .SetHold import SetHoldCls
			self._setHold = SetHoldCls(self._core, self._cmd_group)
		return self._setHold

	@property
	def edge(self):
		"""edge commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_edge'):
			from .Edge import EdgeCls
			self._edge = EdgeCls(self._core, self._cmd_group)
		return self._edge

	@property
	def glitch(self):
		"""glitch commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_glitch'):
			from .Glitch import GlitchCls
			self._glitch = GlitchCls(self._core, self._cmd_group)
		return self._glitch

	@property
	def interval(self):
		"""interval commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_interval'):
			from .Interval import IntervalCls
			self._interval = IntervalCls(self._core, self._cmd_group)
		return self._interval

	@property
	def pattern(self):
		"""pattern commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_pattern'):
			from .Pattern import PatternCls
			self._pattern = PatternCls(self._core, self._cmd_group)
		return self._pattern

	@property
	def runt(self):
		"""runt commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_runt'):
			from .Runt import RuntCls
			self._runt = RuntCls(self._core, self._cmd_group)
		return self._runt

	@property
	def state(self):
		"""state commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def timeout(self):
		"""timeout commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_timeout'):
			from .Timeout import TimeoutCls
			self._timeout = TimeoutCls(self._core, self._cmd_group)
		return self._timeout

	@property
	def slew(self):
		"""slew commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_slew'):
			from .Slew import SlewCls
			self._slew = SlewCls(self._core, self._cmd_group)
		return self._slew

	@property
	def width(self):
		"""width commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_width'):
			from .Width import WidthCls
			self._width = WidthCls(self._core, self._cmd_group)
		return self._width

	@property
	def window(self):
		"""window commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_window'):
			from .Window import WindowCls
			self._window = WindowCls(self._core, self._cmd_group)
		return self._window

	def clone(self) -> 'EventCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = EventCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
