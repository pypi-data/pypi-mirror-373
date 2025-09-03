from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StatusCls:
	"""Status commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("status", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, word=repcap.Word.Default) -> enums.SbusMilstdFrameState:
		"""SBUS<*>:MILStd:WORD<*>:STATus \n
		Snippet: value: enums.SbusMilstdFrameState = driver.sbus.milstd.word.status.get(serialBus = repcap.SerialBus.Default, word = repcap.Word.Default) \n
		Returns the overall state of the selected word. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param word: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Word')
			:return: frame_state: OK: the word is valid. SYNC: synchronization error occured. MANC: manchester coding error occured. PAR: parity error occured. GAP: timing gap error occured. RT: remote terminal error occured. INComplete: the sequence is not completely contained in the acquisition UNKNown: unknown frame type"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		word_cmd_val = self._cmd_group.get_repcap_cmd_value(word, repcap.Word)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:MILStd:WORD{word_cmd_val}:STATus?')
		return Conversions.str_to_scalar_enum(response, enums.SbusMilstdFrameState)
