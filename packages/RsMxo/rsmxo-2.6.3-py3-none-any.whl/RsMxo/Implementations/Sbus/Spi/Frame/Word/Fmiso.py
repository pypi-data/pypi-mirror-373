from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.Utilities import trim_str_response
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FmisoCls:
	"""Fmiso commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fmiso", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, word=repcap.Word.Default) -> str:
		"""SBUS<*>:SPI:FRAMe<*>:WORD<*>:FMISo \n
		Snippet: value: str = driver.sbus.spi.frame.word.fmiso.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, word = repcap.Word.Default) \n
		Returns the formatted value of the specified word on the MISO line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param word: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Word')
			:return: formatted_miso_val: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		word_cmd_val = self._cmd_group.get_repcap_cmd_value(word, repcap.Word)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPI:FRAMe{frame_cmd_val}:WORD{word_cmd_val}:FMISo?')
		return trim_str_response(response)
