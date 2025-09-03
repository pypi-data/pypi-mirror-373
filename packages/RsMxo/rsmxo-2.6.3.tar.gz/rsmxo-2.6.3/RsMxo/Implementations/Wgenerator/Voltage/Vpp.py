from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VppCls:
	"""Vpp commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("vpp", core, parent)

	def set(self, amplitude: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:VOLTage[:VPP] \n
		Snippet: driver.wgenerator.voltage.vpp.set(amplitude = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the amplitude of the waveform. \n
			:param amplitude: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(amplitude)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:VOLTage:VPP {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:VOLTage[:VPP] \n
		Snippet: value: float = driver.wgenerator.voltage.vpp.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the amplitude of the waveform. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: amplitude: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:VOLTage:VPP?')
		return Conversions.str_to_float(response)
