from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, waveform_source: enums.WgenWaveformSource, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:ARBGen[:SOURce] \n
		Snippet: driver.wgenerator.arbGen.source.set(waveform_source = enums.WgenWaveformSource.ARBitrary, waveformGen = repcap.WaveformGen.Default) \n
		Selects the source of the arbitrary waveform. \n
			:param waveform_source: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.enum_scalar_to_str(waveform_source, enums.WgenWaveformSource)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:ARBGen:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.WgenWaveformSource:
		"""WGENerator<*>:ARBGen[:SOURce] \n
		Snippet: value: enums.WgenWaveformSource = driver.wgenerator.arbGen.source.get(waveformGen = repcap.WaveformGen.Default) \n
		Selects the source of the arbitrary waveform. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: waveform_source: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:ARBGen:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.WgenWaveformSource)
