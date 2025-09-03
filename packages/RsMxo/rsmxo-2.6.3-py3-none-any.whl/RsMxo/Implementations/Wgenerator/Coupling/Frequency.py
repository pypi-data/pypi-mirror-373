from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def set(self, cpl_freq: bool, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:COUPling[:FREQuency] \n
		Snippet: driver.wgenerator.coupling.frequency.set(cpl_freq = False, waveformGen = repcap.WaveformGen.Default) \n
		Enables the coupling of all frequency parameters of the generators. \n
			:param cpl_freq: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.bool_to_str(cpl_freq)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:COUPling:FREQuency {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> bool:
		"""WGENerator<*>:COUPling[:FREQuency] \n
		Snippet: value: bool = driver.wgenerator.coupling.frequency.get(waveformGen = repcap.WaveformGen.Default) \n
		Enables the coupling of all frequency parameters of the generators. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: cpl_freq: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:COUPling:FREQuency?')
		return Conversions.str_to_bool(response)
