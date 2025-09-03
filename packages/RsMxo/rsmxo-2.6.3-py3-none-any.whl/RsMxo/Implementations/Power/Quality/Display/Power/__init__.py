from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PowerCls:
	"""Power commands group definition. 6 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("power", core, parent)

	@property
	def waveform(self):
		"""waveform commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_waveform'):
			from .Waveform import WaveformCls
			self._waveform = WaveformCls(self._core, self._cmd_group)
		return self._waveform

	@property
	def apparent(self):
		"""apparent commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_apparent'):
			from .Apparent import ApparentCls
			self._apparent = ApparentCls(self._core, self._cmd_group)
		return self._apparent

	@property
	def pfactor(self):
		"""pfactor commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pfactor'):
			from .Pfactor import PfactorCls
			self._pfactor = PfactorCls(self._core, self._cmd_group)
		return self._pfactor

	@property
	def realPower(self):
		"""realPower commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_realPower'):
			from .RealPower import RealPowerCls
			self._realPower = RealPowerCls(self._core, self._cmd_group)
		return self._realPower

	@property
	def reactive(self):
		"""reactive commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_reactive'):
			from .Reactive import ReactiveCls
			self._reactive = ReactiveCls(self._core, self._cmd_group)
		return self._reactive

	@property
	def phase(self):
		"""phase commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_phase'):
			from .Phase import PhaseCls
			self._phase = PhaseCls(self._core, self._cmd_group)
		return self._phase

	def clone(self) -> 'PowerCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = PowerCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
