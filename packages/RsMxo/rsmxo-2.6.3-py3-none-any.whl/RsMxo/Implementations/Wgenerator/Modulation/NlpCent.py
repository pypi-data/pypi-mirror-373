from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NlpCentCls:
	"""NlpCent commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("nlpCent", core, parent)

	def set(self, level_pct: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:NLPCent \n
		Snippet: driver.wgenerator.modulation.nlpCent.set(level_pct = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the level of the noise in percentage of the set Amplitude output of the signal. \n
			:param level_pct: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(level_pct)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:NLPCent {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:NLPCent \n
		Snippet: value: float = driver.wgenerator.modulation.nlpCent.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the level of the noise in percentage of the set Amplitude output of the signal. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: level_pct: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:NLPCent?')
		return Conversions.str_to_float(response)
