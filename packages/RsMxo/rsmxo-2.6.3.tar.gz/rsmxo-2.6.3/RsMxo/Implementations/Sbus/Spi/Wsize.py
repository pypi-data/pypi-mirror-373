from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WsizeCls:
	"""Wsize commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("wsize", core, parent)

	def set(self, word_length: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPI:WSIZe \n
		Snippet: driver.sbus.spi.wsize.set(word_length = 1, serialBus = repcap.SerialBus.Default) \n
		Sets the word length (or symbol size) , which is the number of bits in a message. The maximum word length is 32 bit. \n
			:param word_length: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(word_length)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPI:WSIZe {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:SPI:WSIZe \n
		Snippet: value: int = driver.sbus.spi.wsize.get(serialBus = repcap.SerialBus.Default) \n
		Sets the word length (or symbol size) , which is the number of bits in a message. The maximum word length is 32 bit. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: word_length: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPI:WSIZe?')
		return Conversions.str_to_int(response)
