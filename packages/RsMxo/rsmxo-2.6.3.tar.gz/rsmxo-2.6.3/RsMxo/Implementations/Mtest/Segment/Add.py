from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AddCls:
	"""Add commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("add", core, parent)

	def set(self, maskTest=repcap.MaskTest.Default, segment=repcap.Segment.Default) -> None:
		"""MTESt<*>:SEGMent<*>:ADD \n
		Snippet: driver.mtest.segment.add.set(maskTest = repcap.MaskTest.Default, segment = repcap.Segment.Default) \n
		Adds a new segment to the selected mask. The segment has no points, use method RsMxo.Mtest.Segment.Point.Add.set to add
		the points. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
		"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:SEGMent{segment_cmd_val}:ADD')

	def set_and_wait(self, maskTest=repcap.MaskTest.Default, segment=repcap.Segment.Default, opc_timeout_ms: int = -1) -> None:
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		"""MTESt<*>:SEGMent<*>:ADD \n
		Snippet: driver.mtest.segment.add.set_and_wait(maskTest = repcap.MaskTest.Default, segment = repcap.Segment.Default) \n
		Adds a new segment to the selected mask. The segment has no points, use method RsMxo.Mtest.Segment.Point.Add.set to add
		the points. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MTESt{maskTest_cmd_val}:SEGMent{segment_cmd_val}:ADD', opc_timeout_ms)
