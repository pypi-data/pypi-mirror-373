from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WgeneratorCls:
	"""Wgenerator commands group definition. 74 total commands, 14 Subgroups, 1 group commands
	Repeated Capability: WaveformGen, default value after init: WaveformGen.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("wgenerator", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_waveformGen_get', 'repcap_waveformGen_set', repcap.WaveformGen.Nr1)

	def repcap_waveformGen_set(self, waveformGen: repcap.WaveformGen) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to WaveformGen.Default.
		Default value after init: WaveformGen.Nr1"""
		self._cmd_group.set_repcap_enum_value(waveformGen)

	def repcap_waveformGen_get(self) -> repcap.WaveformGen:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def arbGen(self):
		"""arbGen commands group. 6 Sub-classes, 1 commands."""
		if not hasattr(self, '_arbGen'):
			from .ArbGen import ArbGenCls
			self._arbGen = ArbGenCls(self._core, self._cmd_group)
		return self._arbGen

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def frequency(self):
		"""frequency commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def period(self):
		"""period commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_period'):
			from .Period import PeriodCls
			self._period = PeriodCls(self._core, self._cmd_group)
		return self._period

	@property
	def burst(self):
		"""burst commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_burst'):
			from .Burst import BurstCls
			self._burst = BurstCls(self._core, self._cmd_group)
		return self._burst

	@property
	def coupling(self):
		"""coupling commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_coupling'):
			from .Coupling import CouplingCls
			self._coupling = CouplingCls(self._core, self._cmd_group)
		return self._coupling

	@property
	def function(self):
		"""function commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_function'):
			from .Function import FunctionCls
			self._function = FunctionCls(self._core, self._cmd_group)
		return self._function

	@property
	def output(self):
		"""output commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_output'):
			from .Output import OutputCls
			self._output = OutputCls(self._core, self._cmd_group)
		return self._output

	@property
	def voltage(self):
		"""voltage commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_voltage'):
			from .Voltage import VoltageCls
			self._voltage = VoltageCls(self._core, self._cmd_group)
		return self._voltage

	@property
	def modulation(self):
		"""modulation commands group. 11 Sub-classes, 0 commands."""
		if not hasattr(self, '_modulation'):
			from .Modulation import ModulationCls
			self._modulation = ModulationCls(self._core, self._cmd_group)
		return self._modulation

	@property
	def sweep(self):
		"""sweep commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_sweep'):
			from .Sweep import SweepCls
			self._sweep = SweepCls(self._core, self._cmd_group)
		return self._sweep

	@property
	def goverload(self):
		"""goverload commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_goverload'):
			from .Goverload import GoverloadCls
			self._goverload = GoverloadCls(self._core, self._cmd_group)
		return self._goverload

	@property
	def temperature(self):
		"""temperature commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_temperature'):
			from .Temperature import TemperatureCls
			self._temperature = TemperatureCls(self._core, self._cmd_group)
		return self._temperature

	def preset(self, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:PRESet \n
		Snippet: driver.wgenerator.preset(waveformGen = repcap.WaveformGen.Default) \n
		Presets the generator to a default setup. The default includes the following settings:
			- Function type = Sine
			- Frequency = 1 MHz
			- Amplitude = 1 Vpp  \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:PRESet')

	def preset_and_wait(self, waveformGen=repcap.WaveformGen.Default, opc_timeout_ms: int = -1) -> None:
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		"""WGENerator<*>:PRESet \n
		Snippet: driver.wgenerator.preset_and_wait(waveformGen = repcap.WaveformGen.Default) \n
		Presets the generator to a default setup. The default includes the following settings:
			- Function type = Sine
			- Frequency = 1 MHz
			- Amplitude = 1 Vpp  \n
		Same as preset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'WGENerator{waveformGen_cmd_val}:PRESet', opc_timeout_ms)

	def clone(self) -> 'WgeneratorCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = WgeneratorCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
