from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MeasurementCls:
	"""Measurement commands group definition. 86 total commands, 24 Subgroups, 1 group commands
	Repeated Capability: MeasIndex, default value after init: MeasIndex.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("measurement", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_measIndex_get', 'repcap_measIndex_set', repcap.MeasIndex.Nr1)

	def repcap_measIndex_set(self, measIndex: repcap.MeasIndex) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to MeasIndex.Default.
		Default value after init: MeasIndex.Nr1"""
		self._cmd_group.set_repcap_enum_value(measIndex)

	def repcap_measIndex_get(self) -> repcap.MeasIndex:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def main(self):
		"""main commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_main'):
			from .Main import MainCls
			self._main = MainCls(self._core, self._cmd_group)
		return self._main

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def jitter(self):
		"""jitter commands group. 7 Sub-classes, 0 commands."""
		if not hasattr(self, '_jitter'):
			from .Jitter import JitterCls
			self._jitter = JitterCls(self._core, self._cmd_group)
		return self._jitter

	@property
	def protocol(self):
		"""protocol commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_protocol'):
			from .Protocol import ProtocolCls
			self._protocol = ProtocolCls(self._core, self._cmd_group)
		return self._protocol

	@property
	def count(self):
		"""count commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_count'):
			from .Count import CountCls
			self._count = CountCls(self._core, self._cmd_group)
		return self._count

	@property
	def mnoMeas(self):
		"""mnoMeas commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mnoMeas'):
			from .MnoMeas import MnoMeasCls
			self._mnoMeas = MnoMeasCls(self._core, self._cmd_group)
		return self._mnoMeas

	@property
	def shLimits(self):
		"""shLimits commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_shLimits'):
			from .ShLimits import ShLimitsCls
			self._shLimits = ShLimitsCls(self._core, self._cmd_group)
		return self._shLimits

	@property
	def detThreshold(self):
		"""detThreshold commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_detThreshold'):
			from .DetThreshold import DetThresholdCls
			self._detThreshold = DetThresholdCls(self._core, self._cmd_group)
		return self._detThreshold

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def active(self):
		"""active commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_active'):
			from .Active import ActiveCls
			self._active = ActiveCls(self._core, self._cmd_group)
		return self._active

	@property
	def multiple(self):
		"""multiple commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_multiple'):
			from .Multiple import MultipleCls
			self._multiple = MultipleCls(self._core, self._cmd_group)
		return self._multiple

	@property
	def envSelect(self):
		"""envSelect commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_envSelect'):
			from .EnvSelect import EnvSelectCls
			self._envSelect = EnvSelectCls(self._core, self._cmd_group)
		return self._envSelect

	@property
	def fsrc(self):
		"""fsrc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fsrc'):
			from .Fsrc import FsrcCls
			self._fsrc = FsrcCls(self._core, self._cmd_group)
		return self._fsrc

	@property
	def ssrc(self):
		"""ssrc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ssrc'):
			from .Ssrc import SsrcCls
			self._ssrc = SsrcCls(self._core, self._cmd_group)
		return self._ssrc

	@property
	def gate(self):
		"""gate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_gate'):
			from .Gate import GateCls
			self._gate = GateCls(self._core, self._cmd_group)
		return self._gate

	@property
	def limit(self):
		"""limit commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_limit'):
			from .Limit import LimitCls
			self._limit = LimitCls(self._core, self._cmd_group)
		return self._limit

	@property
	def margin(self):
		"""margin commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_margin'):
			from .Margin import MarginCls
			self._margin = MarginCls(self._core, self._cmd_group)
		return self._margin

	@property
	def imprecise(self):
		"""imprecise commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_imprecise'):
			from .Imprecise import ImpreciseCls
			self._imprecise = ImpreciseCls(self._core, self._cmd_group)
		return self._imprecise

	@property
	def ampTime(self):
		"""ampTime commands group. 9 Sub-classes, 0 commands."""
		if not hasattr(self, '_ampTime'):
			from .AmpTime import AmpTimeCls
			self._ampTime = AmpTimeCls(self._core, self._cmd_group)
		return self._ampTime

	@property
	def display(self):
		"""display commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def track(self):
		"""track commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_track'):
			from .Track import TrackCls
			self._track = TrackCls(self._core, self._cmd_group)
		return self._track

	@property
	def refLevel(self):
		"""refLevel commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_refLevel'):
			from .RefLevel import RefLevelCls
			self._refLevel = RefLevelCls(self._core, self._cmd_group)
		return self._refLevel

	@property
	def result(self):
		"""result commands group. 11 Sub-classes, 0 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def statistics(self):
		"""statistics commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_statistics'):
			from .Statistics import StatisticsCls
			self._statistics = StatisticsCls(self._core, self._cmd_group)
		return self._statistics

	def clear(self, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:CLEar \n
		Snippet: driver.measurement.clear(measIndex = repcap.MeasIndex.Default) \n
		Deletes the results of all measurements. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:CLEar')

	def clear_and_wait(self, measIndex=repcap.MeasIndex.Default, opc_timeout_ms: int = -1) -> None:
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		"""MEASurement<*>:CLEar \n
		Snippet: driver.measurement.clear_and_wait(measIndex = repcap.MeasIndex.Default) \n
		Deletes the results of all measurements. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MEASurement{measIndex_cmd_val}:CLEar', opc_timeout_ms)

	def clone(self) -> 'MeasurementCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MeasurementCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
