from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ItimeCls:
	"""Itime commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("itime", core, parent)

	def set(self, idle_time: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:BURSt:ITIMe \n
		Snippet: driver.wgenerator.burst.itime.set(idle_time = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param idle_time: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(idle_time)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:BURSt:ITIMe {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:BURSt:ITIMe \n
		Snippet: value: float = driver.wgenerator.burst.itime.get(waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: idle_time: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:BURSt:ITIMe?')
		return Conversions.str_to_float(response)
