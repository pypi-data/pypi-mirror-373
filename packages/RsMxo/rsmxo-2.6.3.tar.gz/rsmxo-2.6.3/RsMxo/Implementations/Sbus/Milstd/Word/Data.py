from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Utilities import trim_str_response
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DataCls:
	"""Data commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, word=repcap.Word.Default) -> str:
		"""SBUS<*>:MILStd:WORD<*>:DATA \n
		Snippet: value: str = driver.sbus.milstd.word.data.get(serialBus = repcap.SerialBus.Default, word = repcap.Word.Default) \n
		Return the data pattern of the specified word. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param word: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Word')
			:return: frm_dat_patt: List of comma separated values."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		word_cmd_val = self._cmd_group.get_repcap_cmd_value(word, repcap.Word)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:MILStd:WORD{word_cmd_val}:DATA?')
		return trim_str_response(response)
