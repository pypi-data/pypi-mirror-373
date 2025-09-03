from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HighCls:
	"""High commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("high", core, parent)

	def set(self, high: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:VOLTage:HIGH \n
		Snippet: driver.wgenerator.voltage.high.set(high = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the high signal level of the output waveform. \n
			:param high: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(high)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:VOLTage:HIGH {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:VOLTage:HIGH \n
		Snippet: value: float = driver.wgenerator.voltage.high.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the high signal level of the output waveform. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: high: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:VOLTage:HIGH?')
		return Conversions.str_to_float(response)
