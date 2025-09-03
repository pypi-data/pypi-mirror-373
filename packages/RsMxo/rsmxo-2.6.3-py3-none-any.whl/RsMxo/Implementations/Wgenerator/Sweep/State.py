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

	def set(self, sweep: bool, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:SWEep[:STATe] \n
		Snippet: driver.wgenerator.sweep.state.set(sweep = False, waveformGen = repcap.WaveformGen.Default) \n
		Enables or disables the sweeping. \n
			:param sweep: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.bool_to_str(sweep)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:SWEep:STATe {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> bool:
		"""WGENerator<*>:SWEep[:STATe] \n
		Snippet: value: bool = driver.wgenerator.sweep.state.get(waveformGen = repcap.WaveformGen.Default) \n
		Enables or disables the sweeping. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: sweep: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:SWEep:STATe?')
		return Conversions.str_to_bool(response)
