from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class InversionCls:
	"""Inversion commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("inversion", core, parent)

	def set(self, inversion: bool, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:VOLTage:INVersion \n
		Snippet: driver.wgenerator.voltage.inversion.set(inversion = False, waveformGen = repcap.WaveformGen.Default) \n
		Inverts the waveform at the offset level. \n
			:param inversion: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.bool_to_str(inversion)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:VOLTage:INVersion {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> bool:
		"""WGENerator<*>:VOLTage:INVersion \n
		Snippet: value: bool = driver.wgenerator.voltage.inversion.get(waveformGen = repcap.WaveformGen.Default) \n
		Inverts the waveform at the offset level. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: inversion: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:VOLTage:INVersion?')
		return Conversions.str_to_bool(response)
