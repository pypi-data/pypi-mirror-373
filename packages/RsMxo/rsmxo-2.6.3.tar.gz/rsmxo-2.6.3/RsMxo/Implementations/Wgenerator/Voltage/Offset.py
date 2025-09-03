from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OffsetCls:
	"""Offset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	def set(self, offset: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:VOLTage:OFFSet \n
		Snippet: driver.wgenerator.voltage.offset.set(offset = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the vertical offset of the generated waveform. \n
			:param offset: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(offset)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:VOLTage:OFFSet {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:VOLTage:OFFSet \n
		Snippet: value: float = driver.wgenerator.voltage.offset.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the vertical offset of the generated waveform. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: offset: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:VOLTage:OFFSet?')
		return Conversions.str_to_float(response)
