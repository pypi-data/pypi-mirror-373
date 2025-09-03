from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FendCls:
	"""Fend commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fend", core, parent)

	def set(self, stop_frequency: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:SWEep:FEND \n
		Snippet: driver.wgenerator.sweep.fend.set(stop_frequency = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the stop frequency of the sweep signal. \n
			:param stop_frequency: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(stop_frequency)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:SWEep:FEND {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:SWEep:FEND \n
		Snippet: value: float = driver.wgenerator.sweep.fend.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the stop frequency of the sweep signal. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: stop_frequency: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:SWEep:FEND?')
		return Conversions.str_to_float(response)
