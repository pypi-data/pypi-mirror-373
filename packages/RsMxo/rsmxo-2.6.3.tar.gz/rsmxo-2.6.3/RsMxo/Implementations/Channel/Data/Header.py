from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.StructBase import StructBase
from ....Internal.ArgStruct import ArgStruct
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HeaderCls:
	"""Header commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("header", core, parent)

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Xstart: float: 1. header value: start time XStart in s
			- 2 Xstop: float: 2. header value: end time XStop in s
			- 3 Record_Length: int: 3. header value: record length of the waveform in samples
			- 4 Vals_Per_Smp: int: 4. header value: number of values per sample interval. For most waveforms, the result is 1. For peak detect and envelope waveforms, it is 2. If the number is 2, the number of returned values is twice the number of samples (record length) ."""
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

	def get(self, channel=repcap.Channel.Default) -> GetStruct:
		"""CHANnel<*>:DATA:HEADer \n
		Snippet: value: GetStruct = driver.channel.data.header.get(channel = repcap.Channel.Default) \n
		Returns the header of channel waveform data, the attributes of the waveform. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		return self._core.io.query_struct(f'CHANnel{channel_cmd_val}:DATA:HEADer?', self.__class__.GetStruct())
