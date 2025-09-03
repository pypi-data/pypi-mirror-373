from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TxValueCls:
	"""TxValue commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("txValue", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, word=repcap.Word.Default) -> int:
		"""SBUS<*>:UART:WORD<*>:TXValue \n
		Snippet: value: int = driver.sbus.uart.word.txValue.get(serialBus = repcap.SerialBus.Default, word = repcap.Word.Default) \n
		Returns the value of the specified word on the TX line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param word: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Word')
			:return: tx_value: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		word_cmd_val = self._cmd_group.get_repcap_cmd_value(word, repcap.Word)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:WORD{word_cmd_val}:TXValue?')
		return Conversions.str_to_int(response)
