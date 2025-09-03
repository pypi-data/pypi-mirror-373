from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LowCls:
	"""Low commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("low", core, parent)

	def set(self, low: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:VOLTage:LOW \n
		Snippet: driver.wgenerator.voltage.low.set(low = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the low signal level of the output waveform. \n
			:param low: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(low)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:VOLTage:LOW {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:VOLTage:LOW \n
		Snippet: value: float = driver.wgenerator.voltage.low.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the low signal level of the output waveform. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: low: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:VOLTage:LOW?')
		return Conversions.str_to_float(response)
