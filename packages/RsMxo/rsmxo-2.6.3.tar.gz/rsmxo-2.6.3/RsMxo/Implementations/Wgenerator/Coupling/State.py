from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, couple_enable: bool, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:COUPling:STATe \n
		Snippet: driver.wgenerator.coupling.state.set(couple_enable = False, waveformGen = repcap.WaveformGen.Default) \n
		Enables the coupling of the generators with the selected set of parameters: amplitude and frequency. \n
			:param couple_enable: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.bool_to_str(couple_enable)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:COUPling:STATe {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> bool:
		"""WGENerator<*>:COUPling:STATe \n
		Snippet: value: bool = driver.wgenerator.coupling.state.get(waveformGen = repcap.WaveformGen.Default) \n
		Enables the coupling of the generators with the selected set of parameters: amplitude and frequency. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: couple_enable: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:COUPling:STATe?')
		return Conversions.str_to_bool(response)
