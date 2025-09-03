from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValidCls:
	"""Valid commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("valid", core, parent)

	def get(self, maskTest=repcap.MaskTest.Default, segment=repcap.Segment.Default) -> bool:
		"""MTESt<*>:SEGMent<*>:VALid \n
		Snippet: value: bool = driver.mtest.segment.valid.get(maskTest = repcap.MaskTest.Default, segment = repcap.Segment.Default) \n
		Checks the validity of the indicated segment. The segment is invalid if one of its points is invalid.
		See 'Mask Definition'. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:return: valid: ON = valid OFF = invalid"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:SEGMent{segment_cmd_val}:VALid?')
		return Conversions.str_to_bool(response)
