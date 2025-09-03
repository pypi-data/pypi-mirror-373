from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DepthCls:
	"""Depth commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("depth", core, parent)

	def set(self, depth: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:AM:DEPTh \n
		Snippet: driver.wgenerator.modulation.am.depth.set(depth = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the modulation depth, the percentage of the amplitude range that is used for AM modulation. \n
			:param depth: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(depth)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:AM:DEPTh {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:AM:DEPTh \n
		Snippet: value: float = driver.wgenerator.modulation.am.depth.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the modulation depth, the percentage of the amplitude range that is used for AM modulation. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: depth: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:AM:DEPTh?')
		return Conversions.str_to_float(response)
