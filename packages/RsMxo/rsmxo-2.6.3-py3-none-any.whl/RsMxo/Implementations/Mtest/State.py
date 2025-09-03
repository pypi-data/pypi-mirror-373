from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:STATe \n
		Snippet: driver.mtest.state.set(state = False, maskTest = repcap.MaskTest.Default) \n
		Activates or deactivates the mask test. \n
			:param state: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.bool_to_str(state)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:STATe {param}')

	def get(self, maskTest=repcap.MaskTest.Default) -> bool:
		"""MTESt<*>:STATe \n
		Snippet: value: bool = driver.mtest.state.get(maskTest = repcap.MaskTest.Default) \n
		Activates or deactivates the mask test. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: state: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
