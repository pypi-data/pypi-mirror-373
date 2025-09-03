from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DcLevelCls:
	"""DcLevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dcLevel", core, parent)

	def set(self, dc_level: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:VOLTage:DCLevel \n
		Snippet: driver.wgenerator.voltage.dcLevel.set(dc_level = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the level for the DC signal, if method RsMxo.Wgenerator.Function.Select.set is set to DC. \n
			:param dc_level: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(dc_level)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:VOLTage:DCLevel {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:VOLTage:DCLevel \n
		Snippet: value: float = driver.wgenerator.voltage.dcLevel.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the level for the DC signal, if method RsMxo.Wgenerator.Function.Select.set is set to DC. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: dc_level: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:VOLTage:DCLevel?')
		return Conversions.str_to_float(response)
