from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ArbGenCls:
	"""ArbGen commands group definition. 7 total commands, 6 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("arbGen", core, parent)

	@property
	def runSingle(self):
		"""runSingle commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_runSingle'):
			from .RunSingle import RunSingleCls
			self._runSingle = RunSingleCls(self._core, self._cmd_group)
		return self._runSingle

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def runMode(self):
		"""runMode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_runMode'):
			from .RunMode import RunModeCls
			self._runMode = RunModeCls(self._core, self._cmd_group)
		return self._runMode

	@property
	def symbolRate(self):
		"""symbolRate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symbolRate'):
			from .SymbolRate import SymbolRateCls
			self._symbolRate = SymbolRateCls(self._core, self._cmd_group)
		return self._symbolRate

	@property
	def samples(self):
		"""samples commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_samples'):
			from .Samples import SamplesCls
			self._samples = SamplesCls(self._core, self._cmd_group)
		return self._samples

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	def open(self, waveformGen=repcap.WaveformGen.Default, opc_timeout_ms: int = -1) -> None:
		"""WGENerator<*>:ARBGen:OPEN \n
		Snippet: driver.wgenerator.arbGen.open(waveformGen = repcap.WaveformGen.Default) \n
		Loads the arbitrary waveform, which is selected with the method RsMxo.Wgenerator.ArbGen.Name.set command. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write_with_opc(f'WGENerator{waveformGen_cmd_val}:ARBGen:OPEN', opc_timeout_ms)
		# OpcSyncAllowed = true

	def clone(self) -> 'ArbGenCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ArbGenCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
