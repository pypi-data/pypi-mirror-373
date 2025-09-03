from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NoiseCls:
	"""Noise commands group definition. 6 total commands, 6 Subgroups, 0 group commands
	Repeated Capability: Noise, default value after init: Noise.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("noise", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_noise_get', 'repcap_noise_set', repcap.Noise.Nr1)

	def repcap_noise_set(self, noise: repcap.Noise) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Noise.Default.
		Default value after init: Noise.Nr1"""
		self._cmd_group.set_repcap_enum_value(noise)

	def repcap_noise_get(self) -> repcap.Noise:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def absolute(self):
		"""absolute commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_absolute'):
			from .Absolute import AbsoluteCls
			self._absolute = AbsoluteCls(self._core, self._cmd_group)
		return self._absolute

	@property
	def mode(self):
		"""mode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import ModeCls
			self._mode = ModeCls(self._core, self._cmd_group)
		return self._mode

	@property
	def relative(self):
		"""relative commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_relative'):
			from .Relative import RelativeCls
			self._relative = RelativeCls(self._core, self._cmd_group)
		return self._relative

	@property
	def effective(self):
		"""effective commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_effective'):
			from .Effective import EffectiveCls
			self._effective = EffectiveCls(self._core, self._cmd_group)
		return self._effective

	@property
	def perDivision(self):
		"""perDivision commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_perDivision'):
			from .PerDivision import PerDivisionCls
			self._perDivision = PerDivisionCls(self._core, self._cmd_group)
		return self._perDivision

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	def clone(self) -> 'NoiseCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = NoiseCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
