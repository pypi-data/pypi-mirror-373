from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NameCls:
	"""Name commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("name", core, parent)

	def set(self, name: str, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:IMEXport:NAME \n
		Snippet: driver.mtest.imExport.name.set(name = 'abc', maskTest = repcap.MaskTest.Default) \n
		Sets the path, the filename and the file format of the mask file. \n
			:param name: String with path and file name with extension .xml.
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.value_to_quoted_str(name)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:IMEXport:NAME {param}')

	def get(self, maskTest=repcap.MaskTest.Default) -> str:
		"""MTESt<*>:IMEXport:NAME \n
		Snippet: value: str = driver.mtest.imExport.name.get(maskTest = repcap.MaskTest.Default) \n
		Sets the path, the filename and the file format of the mask file. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: name: String with path and file name with extension .xml."""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:IMEXport:NAME?')
		return trim_str_response(response)
