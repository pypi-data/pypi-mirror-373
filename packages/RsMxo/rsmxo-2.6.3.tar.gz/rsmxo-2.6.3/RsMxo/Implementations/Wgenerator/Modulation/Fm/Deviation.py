from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DeviationCls:
	"""Deviation commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("deviation", core, parent)

	def set(self, deviation: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:FM:DEViation \n
		Snippet: driver.wgenerator.modulation.fm.deviation.set(deviation = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency deviation, the maximum difference between the FM modulated signal and the carrier signal. \n
			:param deviation: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(deviation)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:FM:DEViation {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:FM:DEViation \n
		Snippet: value: float = driver.wgenerator.modulation.fm.deviation.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency deviation, the maximum difference between the FM modulated signal and the carrier signal. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: deviation: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:FM:DEViation?')
		return Conversions.str_to_float(response)
