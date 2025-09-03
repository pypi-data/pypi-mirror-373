from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HarmonicsCls:
	"""Harmonics commands group definition. 41 total commands, 12 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("harmonics", core, parent)

	@property
	def standard(self):
		"""standard commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_standard'):
			from .Standard import StandardCls
			self._standard = StandardCls(self._core, self._cmd_group)
		return self._standard

	@property
	def revision(self):
		"""revision commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_revision'):
			from .Revision import RevisionCls
			self._revision = RevisionCls(self._core, self._cmd_group)
		return self._revision

	@property
	def available(self):
		"""available commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_available'):
			from .Available import AvailableCls
			self._available = AvailableCls(self._core, self._cmd_group)
		return self._available

	@property
	def pfactor(self):
		"""pfactor commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_pfactor'):
			from .Pfactor import PfactorCls
			self._pfactor = PfactorCls(self._core, self._cmd_group)
		return self._pfactor

	@property
	def rpower(self):
		"""rpower commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_rpower'):
			from .Rpower import RpowerCls
			self._rpower = RpowerCls(self._core, self._cmd_group)
		return self._rpower

	@property
	def source(self):
		"""source commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def frequency(self):
		"""frequency commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def result(self):
		"""result commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def measurement(self):
		"""measurement commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_measurement'):
			from .Measurement import MeasurementCls
			self._measurement = MeasurementCls(self._core, self._cmd_group)
		return self._measurement

	@property
	def display(self):
		"""display commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def refLevel(self):
		"""refLevel commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_refLevel'):
			from .RefLevel import RefLevelCls
			self._refLevel = RefLevelCls(self._core, self._cmd_group)
		return self._refLevel

	@property
	def power(self):
		"""power commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_power'):
			from .Power import PowerCls
			self._power = PowerCls(self._core, self._cmd_group)
		return self._power

	def clone(self) -> 'HarmonicsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = HarmonicsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
