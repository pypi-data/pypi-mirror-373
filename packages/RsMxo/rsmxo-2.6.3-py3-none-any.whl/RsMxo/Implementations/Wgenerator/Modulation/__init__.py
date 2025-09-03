from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModulationCls:
	"""Modulation commands group definition. 26 total commands, 11 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("modulation", core, parent)

	@property
	def noise(self):
		"""noise commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_noise'):
			from .Noise import NoiseCls
			self._noise = NoiseCls(self._core, self._cmd_group)
		return self._noise

	@property
	def nlpCent(self):
		"""nlpCent commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_nlpCent'):
			from .NlpCent import NlpCentCls
			self._nlpCent = NlpCentCls(self._core, self._cmd_group)
		return self._nlpCent

	@property
	def nlAbsolute(self):
		"""nlAbsolute commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_nlAbsolute'):
			from .NlAbsolute import NlAbsoluteCls
			self._nlAbsolute = NlAbsoluteCls(self._core, self._cmd_group)
		return self._nlAbsolute

	@property
	def ndcLevel(self):
		"""ndcLevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ndcLevel'):
			from .NdcLevel import NdcLevelCls
			self._ndcLevel = NdcLevelCls(self._core, self._cmd_group)
		return self._ndcLevel

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def carrier(self):
		"""carrier commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_carrier'):
			from .Carrier import CarrierCls
			self._carrier = CarrierCls(self._core, self._cmd_group)
		return self._carrier

	@property
	def am(self):
		"""am commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_am'):
			from .Am import AmCls
			self._am = AmCls(self._core, self._cmd_group)
		return self._am

	@property
	def fm(self):
		"""fm commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_fm'):
			from .Fm import FmCls
			self._fm = FmCls(self._core, self._cmd_group)
		return self._fm

	@property
	def pwm(self):
		"""pwm commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_pwm'):
			from .Pwm import PwmCls
			self._pwm = PwmCls(self._core, self._cmd_group)
		return self._pwm

	@property
	def fsk(self):
		"""fsk commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_fsk'):
			from .Fsk import FskCls
			self._fsk = FskCls(self._core, self._cmd_group)
		return self._fsk

	def clone(self) -> 'ModulationCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ModulationCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
