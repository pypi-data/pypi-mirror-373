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

	def set(self, frequency: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:PWM:FREQuency \n
		Snippet: driver.wgenerator.modulation.pwm.frequency.set(frequency = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency of the modulating waveform for PWM modulation. \n
			:param frequency: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(frequency)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:PWM:FREQuency {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:PWM:FREQuency \n
		Snippet: value: float = driver.wgenerator.modulation.pwm.frequency.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency of the modulating waveform for PWM modulation. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: frequency: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:PWM:FREQuency?')
		return Conversions.str_to_float(response)
