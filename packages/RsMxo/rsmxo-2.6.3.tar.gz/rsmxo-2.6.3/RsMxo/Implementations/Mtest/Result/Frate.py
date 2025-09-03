from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrateCls:
	"""Frate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frate", core, parent)

	def get(self, maskTest=repcap.MaskTest.Default) -> float:
		"""MTESt<*>:RESult:FRATe \n
		Snippet: value: float = driver.mtest.result.frate.get(maskTest = repcap.MaskTest.Default) \n
		Returns the fail rate, the ratio of failed acquisitions to the number of tested acquisitions. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: fail_rate: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:RESult:FRATe?')
		return Conversions.str_to_float(response)
