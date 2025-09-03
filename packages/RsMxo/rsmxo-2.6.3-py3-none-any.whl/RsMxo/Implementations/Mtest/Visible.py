from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VisibleCls:
	"""Visible commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("visible", core, parent)

	def set(self, display_state: bool, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:VISible \n
		Snippet: driver.mtest.visible.set(display_state = False, maskTest = repcap.MaskTest.Default) \n
		Displays all mask segments of the selected mask in the diagrams, or hides them. \n
			:param display_state: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.bool_to_str(display_state)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:VISible {param}')

	def get(self, maskTest=repcap.MaskTest.Default) -> bool:
		"""MTESt<*>:VISible \n
		Snippet: value: bool = driver.mtest.visible.get(maskTest = repcap.MaskTest.Default) \n
		Displays all mask segments of the selected mask in the diagrams, or hides them. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: display_state: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:VISible?')
		return Conversions.str_to_bool(response)
