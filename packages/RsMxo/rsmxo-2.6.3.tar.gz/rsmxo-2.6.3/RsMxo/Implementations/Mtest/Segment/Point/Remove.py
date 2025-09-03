from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RemoveCls:
	"""Remove commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("remove", core, parent)

	def set(self, maskTest=repcap.MaskTest.Default, segment=repcap.Segment.Default, point=repcap.Point.Default) -> None:
		"""MTESt<*>:SEGMent<*>:POINt<*>:REMove \n
		Snippet: driver.mtest.segment.point.remove.set(maskTest = repcap.MaskTest.Default, segment = repcap.Segment.Default, point = repcap.Point.Default) \n
		Deletes the indicated corner point of the mask segment. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
		"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:SEGMent{segment_cmd_val}:POINt{point_cmd_val}:REMove')

	def set_and_wait(self, maskTest=repcap.MaskTest.Default, segment=repcap.Segment.Default, point=repcap.Point.Default, opc_timeout_ms: int = -1) -> None:
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		"""MTESt<*>:SEGMent<*>:POINt<*>:REMove \n
		Snippet: driver.mtest.segment.point.remove.set_and_wait(maskTest = repcap.MaskTest.Default, segment = repcap.Segment.Default, point = repcap.Point.Default) \n
		Deletes the indicated corner point of the mask segment. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MTESt{maskTest_cmd_val}:SEGMent{segment_cmd_val}:POINt{point_cmd_val}:REMove', opc_timeout_ms)
