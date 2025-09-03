from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NdcLevelCls:
	"""NdcLevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ndcLevel", core, parent)

	def set(self, level_dc: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:NDCLevel \n
		Snippet: driver.wgenerator.modulation.ndcLevel.set(level_dc = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the DC noise level, if method RsMxo.Wgenerator.Function.Select.set is set to DC. \n
			:param level_dc: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(level_dc)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:NDCLevel {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:NDCLevel \n
		Snippet: value: float = driver.wgenerator.modulation.ndcLevel.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the DC noise level, if method RsMxo.Wgenerator.Function.Select.set is set to DC. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: level_dc: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:NDCLevel?')
		return Conversions.str_to_float(response)
