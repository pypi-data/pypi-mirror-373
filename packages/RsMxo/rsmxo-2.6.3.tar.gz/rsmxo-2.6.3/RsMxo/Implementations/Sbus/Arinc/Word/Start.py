from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StartCls:
	"""Start commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("start", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, word=repcap.Word.Default) -> float:
		"""SBUS<*>:ARINc:WORD<*>:STARt \n
		Snippet: value: float = driver.sbus.arinc.word.start.get(serialBus = repcap.SerialBus.Default, word = repcap.Word.Default) \n
		Returns the start time of the specified word. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param word: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Word')
			:return: frame_start: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		word_cmd_val = self._cmd_group.get_repcap_cmd_value(word, repcap.Word)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:WORD{word_cmd_val}:STARt?')
		return Conversions.str_to_float(response)
