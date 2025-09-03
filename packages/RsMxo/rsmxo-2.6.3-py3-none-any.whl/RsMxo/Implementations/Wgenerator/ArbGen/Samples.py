from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SamplesCls:
	"""Samples commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("samples", core, parent)

	def get(self, waveformGen=repcap.WaveformGen.Default) -> int:
		"""WGENerator<*>:ARBGen:SAMPles \n
		Snippet: value: int = driver.wgenerator.arbGen.samples.get(waveformGen = repcap.WaveformGen.Default) \n
		Returns the number of samples in the loaded waveform. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: num_samples: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:ARBGen:SAMPles?')
		return Conversions.str_to_int(response)
