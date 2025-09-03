from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WaveformsCls:
	"""Waveforms commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("waveforms", core, parent)

	def get(self, maskTest=repcap.MaskTest.Default) -> int:
		"""MTESt<*>:RESult:COUNt:WAVeforms \n
		Snippet: value: int = driver.mtest.result.count.waveforms.get(maskTest = repcap.MaskTest.Default) \n
		Returns the number of tested acquisitions. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: acqs_completed: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:RESult:COUNt:WAVeforms?')
		return Conversions.str_to_int(response)
