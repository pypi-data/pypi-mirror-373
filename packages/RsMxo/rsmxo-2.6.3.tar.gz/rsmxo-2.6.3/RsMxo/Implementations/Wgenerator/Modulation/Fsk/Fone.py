from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FoneCls:
	"""Fone commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fone", core, parent)

	def set(self, frequency_1: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:FSK:FONE \n
		Snippet: driver.wgenerator.modulation.fsk.fone.set(frequency_1 = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency of the first /second signal in FSK modulated signal. \n
			:param frequency_1: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(frequency_1)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:FSK:FONE {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:FSK:FONE \n
		Snippet: value: float = driver.wgenerator.modulation.fsk.fone.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency of the first /second signal in FSK modulated signal. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: frequency_1: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:FSK:FONE?')
		return Conversions.str_to_float(response)
