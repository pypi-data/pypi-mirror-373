from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CycleCountCls:
	"""CycleCount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cycleCount", core, parent)

	def set(self, cycles: int, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:BURSt:CYCLecount \n
		Snippet: driver.wgenerator.burst.cycleCount.set(cycles = 1, waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param cycles: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(cycles)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:BURSt:CYCLecount {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> int:
		"""WGENerator<*>:BURSt:CYCLecount \n
		Snippet: value: int = driver.wgenerator.burst.cycleCount.get(waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: cycles: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:BURSt:CYCLecount?')
		return Conversions.str_to_int(response)
