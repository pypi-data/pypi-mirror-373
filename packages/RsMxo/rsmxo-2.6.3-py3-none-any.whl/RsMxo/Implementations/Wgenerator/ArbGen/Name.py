from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NameCls:
	"""Name commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("name", core, parent)

	def set(self, folder: str, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:ARBGen:NAME \n
		Snippet: driver.wgenerator.arbGen.name.set(folder = 'abc', waveformGen = repcap.WaveformGen.Default) \n
		Sets the file path and the file for an arbitrary waveform, if method RsMxo.Wgenerator.ArbGen.Source.
		set is set to ARBitrary. \n
			:param folder: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.value_to_quoted_str(folder)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:ARBGen:NAME {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> str:
		"""WGENerator<*>:ARBGen:NAME \n
		Snippet: value: str = driver.wgenerator.arbGen.name.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the file path and the file for an arbitrary waveform, if method RsMxo.Wgenerator.ArbGen.Source.
		set is set to ARBitrary. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: folder: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:ARBGen:NAME?')
		return trim_str_response(response)
