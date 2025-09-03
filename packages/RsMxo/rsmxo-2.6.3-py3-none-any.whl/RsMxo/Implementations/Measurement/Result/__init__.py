from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 14 total commands, 11 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	@property
	def actual(self):
		"""actual commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_actual'):
			from .Actual import ActualCls
			self._actual = ActualCls(self._core, self._cmd_group)
		return self._actual

	@property
	def avg(self):
		"""avg commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_avg'):
			from .Avg import AvgCls
			self._avg = AvgCls(self._core, self._cmd_group)
		return self._avg

	@property
	def evtCount(self):
		"""evtCount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_evtCount'):
			from .EvtCount import EvtCountCls
			self._evtCount = EvtCountCls(self._core, self._cmd_group)
		return self._evtCount

	@property
	def npeak(self):
		"""npeak commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_npeak'):
			from .Npeak import NpeakCls
			self._npeak = NpeakCls(self._core, self._cmd_group)
		return self._npeak

	@property
	def ppeak(self):
		"""ppeak commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ppeak'):
			from .Ppeak import PpeakCls
			self._ppeak = PpeakCls(self._core, self._cmd_group)
		return self._ppeak

	@property
	def rms(self):
		"""rms commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rms'):
			from .Rms import RmsCls
			self._rms = RmsCls(self._core, self._cmd_group)
		return self._rms

	@property
	def stdDev(self):
		"""stdDev commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stdDev'):
			from .StdDev import StdDevCls
			self._stdDev = StdDevCls(self._core, self._cmd_group)
		return self._stdDev

	@property
	def wfmCount(self):
		"""wfmCount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_wfmCount'):
			from .WfmCount import WfmCountCls
			self._wfmCount = WfmCountCls(self._core, self._cmd_group)
		return self._wfmCount

	@property
	def start(self):
		"""start commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_start'):
			from .Start import StartCls
			self._start = StartCls(self._core, self._cmd_group)
		return self._start

	@property
	def stop(self):
		"""stop commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stop'):
			from .Stop import StopCls
			self._stop = StopCls(self._core, self._cmd_group)
		return self._stop

	@property
	def events(self):
		"""events commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_events'):
			from .Events import EventsCls
			self._events = EventsCls(self._core, self._cmd_group)
		return self._events

	def clone(self) -> 'ResultCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ResultCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
