from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def set(self, freq_carrier_alias: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:CARRier:FREQuency \n
		Snippet: driver.wgenerator.modulation.carrier.frequency.set(freq_carrier_alias = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency of the carrier signal for a modulation waveform. \n
			:param freq_carrier_alias: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(freq_carrier_alias)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:CARRier:FREQuency {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:CARRier:FREQuency \n
		Snippet: value: float = driver.wgenerator.modulation.carrier.frequency.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency of the carrier signal for a modulation waveform. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: freq_carrier_alias: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:CARRier:FREQuency?')
		return Conversions.str_to_float(response)
