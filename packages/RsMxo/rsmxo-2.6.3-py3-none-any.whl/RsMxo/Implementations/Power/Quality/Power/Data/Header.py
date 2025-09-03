from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.StructBase import StructBase
from ......Internal.ArgStruct import ArgStruct
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HeaderCls:
	"""Header commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("header", core, parent)

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Xstart: float: 1. header value: start time in s
			- 2 Xstop: float: 2. header value: end time in s
			- 3 Record_Length: int: 3. header value: record length of the waveform in samples
			- 4 Vals_Per_Smp: int: 4. header value: number of values per sample interval. For power quality measurements, the value is 1."""
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

	def get(self, power=repcap.Power.Default) -> GetStruct:
		"""POWer<*>:QUALity:POWer:DATA:HEADer \n
		Snippet: value: GetStruct = driver.power.quality.power.data.header.get(power = repcap.Power.Default) \n
		Returns the header of the power analysis waveform data. The header contains the attributes of the waveform. For power
		harmonics measurements, data is only available if method RsMxo.Power.Harmonics.Standard.set is set to ENC / END. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		return self._core.io.query_struct(f'POWer{power_cmd_val}:QUALity:POWer:DATA:HEADer?', self.__class__.GetStruct())
