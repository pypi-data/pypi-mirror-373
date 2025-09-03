from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SyncCls:
	"""Sync commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sync", core, parent)

	def set(self, initial_phase: enums.InitialPhase, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:PLL:SYNC \n
		Snippet: driver.treference.cdr.software.pll.sync.set(initial_phase = enums.InitialPhase.DATaedge, timingReference = repcap.TimingReference.Default) \n
		Defines the phase reference for the first clock edge. \n
			:param initial_phase: SAMPle: the first clock edge matches the first sample of the waveform at the left border of the display. DATaedge: the first clock edge matches the first edge of the data signal.
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.enum_scalar_to_str(initial_phase, enums.InitialPhase)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:PLL:SYNC {param}')

	# noinspection PyTypeChecker
	def get(self, timingReference=repcap.TimingReference.Default) -> enums.InitialPhase:
		"""TREFerence<*>:CDR:SOFTware:PLL:SYNC \n
		Snippet: value: enums.InitialPhase = driver.treference.cdr.software.pll.sync.get(timingReference = repcap.TimingReference.Default) \n
		Defines the phase reference for the first clock edge. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: initial_phase: SAMPle: the first clock edge matches the first sample of the waveform at the left border of the display. DATaedge: the first clock edge matches the first edge of the data signal."""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:PLL:SYNC?')
		return Conversions.str_to_scalar_enum(response, enums.InitialPhase)
