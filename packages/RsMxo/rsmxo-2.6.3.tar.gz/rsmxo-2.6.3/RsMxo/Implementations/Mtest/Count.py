from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def set(self, count: int, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:COUNt \n
		Snippet: driver.mtest.count.set(count = 1, maskTest = repcap.MaskTest.Default) \n
		Returns the number of masks. MTESt:COUNt? MAX returns the maximum number of masks that can be created. \n
			:param count: Number of defined masks
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.decimal_value_to_str(count)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:COUNt {param}')

	def get(self, maskTest=repcap.MaskTest.Default) -> int:
		"""MTESt<*>:COUNt \n
		Snippet: value: int = driver.mtest.count.get(maskTest = repcap.MaskTest.Default) \n
		Returns the number of masks. MTESt:COUNt? MAX returns the maximum number of masks that can be created. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: count: Number of defined masks"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
