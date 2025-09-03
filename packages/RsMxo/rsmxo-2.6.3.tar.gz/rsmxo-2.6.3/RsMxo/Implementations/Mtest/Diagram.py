from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DiagramCls:
	"""Diagram commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("diagram", core, parent)

	def set(self, sign_diag_key: str, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:DIAGram \n
		Snippet: driver.mtest.diagram.set(sign_diag_key = 'abc', maskTest = repcap.MaskTest.Default) \n
		Sets the layout and the diagram where the mask is located and the test runs. \n
			:param sign_diag_key: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.value_to_quoted_str(sign_diag_key)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:DIAGram {param}')

	def get(self, maskTest=repcap.MaskTest.Default) -> str:
		"""MTESt<*>:DIAGram \n
		Snippet: value: str = driver.mtest.diagram.get(maskTest = repcap.MaskTest.Default) \n
		Sets the layout and the diagram where the mask is located and the test runs. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: sign_diag_key: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:DIAGram?')
		return trim_str_response(response)
