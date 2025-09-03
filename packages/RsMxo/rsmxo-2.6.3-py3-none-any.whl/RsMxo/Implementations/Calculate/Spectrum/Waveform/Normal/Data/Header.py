from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.StructBase import StructBase
from .......Internal.ArgStruct import ArgStruct
from ....... import repcap


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
			- 4 Vals_Per_Smp: int: 4. header value: the number of values per sample interval is always = 1."""
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

	def get(self, spectrum=repcap.Spectrum.Default) -> GetStruct:
		"""CALCulate:SPECtrum<*>:WAVeform:NORMal:DATA:HEADer \n
		Snippet: value: GetStruct = driver.calculate.spectrum.waveform.normal.data.header.get(spectrum = repcap.Spectrum.Default) \n
		Returns the header of spectrum data, the attributes of the waveform. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		return self._core.io.query_struct(f'CALCulate:SPECtrum{spectrum_cmd_val}:WAVeform:NORMal:DATA:HEADer?', self.__class__.GetStruct())
