from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, word=repcap.Word.Default) -> enums.SbusMilstdFrameType:
		"""SBUS<*>:MILStd:WORD<*>:TYPE \n
		Snippet: value: enums.SbusMilstdFrameType = driver.sbus.milstd.word.typePy.get(serialBus = repcap.SerialBus.Default, word = repcap.Word.Default) \n
		Returns the type of the specified word. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param word: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Word')
			:return: frame_type: CMD: command word CMST: command/status word IM: inter message. Shows if there are gap errors or response timeout."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		word_cmd_val = self._cmd_group.get_repcap_cmd_value(word, repcap.Word)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:MILStd:WORD{word_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusMilstdFrameType)
