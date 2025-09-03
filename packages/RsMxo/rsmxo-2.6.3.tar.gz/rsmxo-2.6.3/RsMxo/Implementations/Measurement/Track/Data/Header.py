from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.StructBase import StructBase
from .....Internal.ArgStruct import ArgStruct
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HeaderCls:
	"""Header commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("header", core, parent)

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Xstart: float: 1. header value: start time XStart, acquisition time before trigger, in s
			- 2 Xstop: float: 2. header value: end time XStop, acquisition time after trigger, in s
			- 3 Record_Length: int: 3. header value: number of measured events = number of points in the track waveform
			- 4 Vals_Per_Smp: int: 4. header value: number of values per sample interval. For tracks, the result is always 1."""
		__meta_args_list = [
			ArgStruct.scalar_float('Xstart'),
			ArgStruct.scalar_float('Xstop'),
			ArgStruct.scalar_int('Record_Length'),
			ArgStruct.scalar_int('Vals_Per_Smp')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Xstart: float = None
			self.Xstop: float = None
			self.Record_Length: int = None
			self.Vals_Per_Smp: int = None

	def get(self, measIndex=repcap.MeasIndex.Default) -> GetStruct:
		"""MEASurement<*>:TRACk:DATA:HEADer \n
		Snippet: value: GetStruct = driver.measurement.track.data.header.get(measIndex = repcap.MeasIndex.Default) \n
		Returns the header of track data, the attributes of the waveform. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		return self._core.io.query_struct(f'MEASurement{measIndex_cmd_val}:TRACk:DATA:HEADer?', self.__class__.GetStruct())
