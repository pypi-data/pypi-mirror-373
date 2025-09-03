from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SwitchingCls:
	"""Switching commands group definition. 109 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("switching", core, parent)

	@property
	def display(self):
		"""display commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def source(self):
		"""source commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def region(self):
		"""region commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_region'):
			from .Region import RegionCls
			self._region = RegionCls(self._core, self._cmd_group)
		return self._region

	@property
	def statistics(self):
		"""statistics commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_statistics'):
			from .Statistics import StatisticsCls
			self._statistics = StatisticsCls(self._core, self._cmd_group)
		return self._statistics

	@property
	def result(self):
		"""result commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def power(self):
		"""power commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_power'):
			from .Power import PowerCls
			self._power = PowerCls(self._core, self._cmd_group)
		return self._power

	def clone(self) -> 'SwitchingCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SwitchingCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
