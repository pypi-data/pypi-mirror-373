from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SphaseCls:
	"""Sphase commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sphase", core, parent)

	def set(self, start_phase: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:BURSt:SPHase \n
		Snippet: driver.wgenerator.burst.sphase.set(start_phase = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param start_phase: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(start_phase)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:BURSt:SPHase {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:BURSt:SPHase \n
		Snippet: value: float = driver.wgenerator.burst.sphase.get(waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: start_phase: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:BURSt:SPHase?')
		return Conversions.str_to_float(response)
