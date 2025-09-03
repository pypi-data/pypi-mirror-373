from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RunSingleCls:
	"""RunSingle commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("runSingle", core, parent)

	def set(self, waveformGen=repcap.WaveformGen.Default, opc_timeout_ms: int = -1) -> None:
		"""WGENerator<*>:ARBGen:RUNSingle \n
		Snippet: driver.wgenerator.arbGen.runSingle.set(waveformGen = repcap.WaveformGen.Default) \n
		Executes a single period of the arbitrary signal generator, if method RsMxo.Wgenerator.ArbGen.RunMode.set is set to
		SINGle. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write_with_opc(f'WGENerator{waveformGen_cmd_val}:ARBGen:RUNSingle', opc_timeout_ms)
		# OpcSyncAllowed = true
