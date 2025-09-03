from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, word=repcap.Word.Default) -> enums.SbusUartWordState:
		"""SBUS<*>:UART:WORD<*>:STATe \n
		Snippet: value: enums.SbusUartWordState = driver.sbus.uart.word.state.get(serialBus = repcap.SerialBus.Default, word = repcap.Word.Default) \n
		Returns the status of the specified word. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param word: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Word')
			:return: word_state: OK: the frame is valid. BREak: stop bit error with 0x00 word STERror: start error, incorrect start bit SPERror: stop error, incorrect stop bit PRERror: parity error, incorrect parity bit. INComplete: The frame is not completely contained in the acquisition. The acquired part of the frame is valid."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		word_cmd_val = self._cmd_group.get_repcap_cmd_value(word, repcap.Word)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:WORD{word_cmd_val}:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.SbusUartWordState)
