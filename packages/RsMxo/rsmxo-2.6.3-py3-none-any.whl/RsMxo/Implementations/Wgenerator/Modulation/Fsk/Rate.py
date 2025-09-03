from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RateCls:
	"""Rate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rate", core, parent)

	def set(self, rate: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:FSK[:RATE] \n
		Snippet: driver.wgenerator.modulation.fsk.rate.set(rate = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency at which the signal switches between method RsMxo.Wgenerator.Modulation.Fsk.Fone.set and method RsMxo.
		Wgenerator.Modulation.Fsk.Ftwo.set. \n
			:param rate: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(rate)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:FSK:RATE {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:FSK[:RATE] \n
		Snippet: value: float = driver.wgenerator.modulation.fsk.rate.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the frequency at which the signal switches between method RsMxo.Wgenerator.Modulation.Fsk.Fone.set and method RsMxo.
		Wgenerator.Modulation.Fsk.Ftwo.set. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: rate: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:FSK:RATE?')
		return Conversions.str_to_float(response)
