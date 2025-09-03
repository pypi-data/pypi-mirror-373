from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AmpTimeCls:
	"""AmpTime commands group definition. 10 total commands, 9 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ampTime", core, parent)

	@property
	def pfSlope(self):
		"""pfSlope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pfSlope'):
			from .PfSlope import PfSlopeCls
			self._pfSlope = PfSlopeCls(self._core, self._cmd_group)
		return self._pfSlope

	@property
	def pslope(self):
		"""pslope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pslope'):
			from .Pslope import PslopeCls
			self._pslope = PslopeCls(self._core, self._cmd_group)
		return self._pslope

	@property
	def eslope(self):
		"""eslope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_eslope'):
			from .Eslope import EslopeCls
			self._eslope = EslopeCls(self._core, self._cmd_group)
		return self._eslope

	@property
	def cslope(self):
		"""cslope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_cslope'):
			from .Cslope import CslopeCls
			self._cslope = CslopeCls(self._core, self._cmd_group)
		return self._cslope

	@property
	def ptCount(self):
		"""ptCount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ptCount'):
			from .PtCount import PtCountCls
			self._ptCount = PtCountCls(self._core, self._cmd_group)
		return self._ptCount

	@property
	def result(self):
		"""result commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def delay(self):
		"""delay commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_delay'):
			from .Delay import DelayCls
			self._delay = DelayCls(self._core, self._cmd_group)
		return self._delay

	@property
	def phase(self):
		"""phase commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_phase'):
			from .Phase import PhaseCls
			self._phase = PhaseCls(self._core, self._cmd_group)
		return self._phase

	@property
	def dtoTrigger(self):
		"""dtoTrigger commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_dtoTrigger'):
			from .DtoTrigger import DtoTriggerCls
			self._dtoTrigger = DtoTriggerCls(self._core, self._cmd_group)
		return self._dtoTrigger

	def clone(self) -> 'AmpTimeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AmpTimeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
