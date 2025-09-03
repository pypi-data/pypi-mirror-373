from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SpectrumCls:
	"""Spectrum commands group definition. 57 total commands, 10 Subgroups, 1 group commands
	Repeated Capability: Spectrum, default value after init: Spectrum.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("spectrum", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_spectrum_get', 'repcap_spectrum_set', repcap.Spectrum.Nr1)

	def repcap_spectrum_set(self, spectrum: repcap.Spectrum) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Spectrum.Default.
		Default value after init: Spectrum.Nr1"""
		self._cmd_group.set_repcap_enum_value(spectrum)

	def repcap_spectrum_get(self) -> repcap.Spectrum:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def waveform(self):
		"""waveform commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_waveform'):
			from .Waveform import WaveformCls
			self._waveform = WaveformCls(self._core, self._cmd_group)
		return self._waveform

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def threshold(self):
		"""threshold commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_threshold'):
			from .Threshold import ThresholdCls
			self._threshold = ThresholdCls(self._core, self._cmd_group)
		return self._threshold

	@property
	def pexcursion(self):
		"""pexcursion commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pexcursion'):
			from .Pexcursion import PexcursionCls
			self._pexcursion = PexcursionCls(self._core, self._cmd_group)
		return self._pexcursion

	@property
	def fftLength(self):
		"""fftLength commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fftLength'):
			from .FftLength import FftLengthCls
			self._fftLength = FftLengthCls(self._core, self._cmd_group)
		return self._fftLength

	@property
	def magnitude(self):
		"""magnitude commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_magnitude'):
			from .Magnitude import MagnitudeCls
			self._magnitude = MagnitudeCls(self._core, self._cmd_group)
		return self._magnitude

	@property
	def frequency(self):
		"""frequency commands group. 7 Sub-classes, 0 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def plist(self):
		"""plist commands group. 9 Sub-classes, 0 commands."""
		if not hasattr(self, '_plist'):
			from .Plist import PlistCls
			self._plist = PlistCls(self._core, self._cmd_group)
		return self._plist

	@property
	def gate(self):
		"""gate commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_gate'):
			from .Gate import GateCls
			self._gate = GateCls(self._core, self._cmd_group)
		return self._gate

	def preset(self, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PRESet \n
		Snippet: driver.calculate.spectrum.preset(spectrum = repcap.Spectrum.Default) \n
		Presets the spectrum measurement. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PRESet')

	def preset_and_wait(self, spectrum=repcap.Spectrum.Default, opc_timeout_ms: int = -1) -> None:
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		"""CALCulate:SPECtrum<*>:PRESet \n
		Snippet: driver.calculate.spectrum.preset_and_wait(spectrum = repcap.Spectrum.Default) \n
		Presets the spectrum measurement. \n
		Same as preset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CALCulate:SPECtrum{spectrum_cmd_val}:PRESet', opc_timeout_ms)

	def clone(self) -> 'SpectrumCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SpectrumCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
