from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PowerCls:
	"""Power commands group definition. 293 total commands, 7 Subgroups, 0 group commands
	Repeated Capability: Power, default value after init: Power.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("power", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_power_get', 'repcap_power_set', repcap.Power.Nr1)

	def repcap_power_set(self, power: repcap.Power) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Power.Default.
		Default value after init: Power.Nr1"""
		self._cmd_group.set_repcap_enum_value(power)

	def repcap_power_get(self) -> repcap.Power:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def askew(self):
		"""askew commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_askew'):
			from .Askew import AskewCls
			self._askew = AskewCls(self._core, self._cmd_group)
		return self._askew

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def quality(self):
		"""quality commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_quality'):
			from .Quality import QualityCls
			self._quality = QualityCls(self._core, self._cmd_group)
		return self._quality

	@property
	def harmonics(self):
		"""harmonics commands group. 12 Sub-classes, 0 commands."""
		if not hasattr(self, '_harmonics'):
			from .Harmonics import HarmonicsCls
			self._harmonics = HarmonicsCls(self._core, self._cmd_group)
		return self._harmonics

	@property
	def switching(self):
		"""switching commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_switching'):
			from .Switching import SwitchingCls
			self._switching = SwitchingCls(self._core, self._cmd_group)
		return self._switching

	@property
	def onOff(self):
		"""onOff commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_onOff'):
			from .OnOff import OnOffCls
			self._onOff = OnOffCls(self._core, self._cmd_group)
		return self._onOff

	def clone(self) -> 'PowerCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = PowerCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
