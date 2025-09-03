from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Types import DataType
from .....Internal.StructBase import StructBase
from .....Internal.ArgStruct import ArgStruct
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DataCls:
	"""Data commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Count: int: No parameter help available
			- 2 Values: List[int]: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Count'),
			ArgStruct('Values', DataType.IntegerList, None, False, True, 1)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Count: int = None
			self.Values: List[int] = None

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> GetStruct:
		"""SBUS<*>:I3C:FRAMe<*>:DATA \n
		Snippet: value: GetStruct = driver.sbus.i3C.frame.data.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the data words of the specified frame in comma-separated values. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		return self._core.io.query_struct(f'SBUS{serialBus_cmd_val}:I3C:FRAMe{frame_cmd_val}:DATA?', self.__class__.GetStruct())
