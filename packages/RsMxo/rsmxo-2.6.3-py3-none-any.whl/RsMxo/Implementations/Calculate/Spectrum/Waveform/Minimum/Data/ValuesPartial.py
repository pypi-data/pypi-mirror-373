from typing import List

from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.Types import DataType
from .......Internal.ArgSingleList import ArgSingleList
from .......Internal.ArgSingle import ArgSingle
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValuesPartialCls:
	"""ValuesPartial commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("valuesPartial", core, parent)

	def get(self, offset: int, length: int, spectrum=repcap.Spectrum.Default) -> List[float]:
		"""CALCulate:SPECtrum<*>:WAVeform:MINimum:DATA[:VALues] \n
		Snippet: value: List[float] = driver.calculate.spectrum.waveform.minimum.data.valuesPartial.get(offset = 1, length = 1, spectrum = repcap.Spectrum.Default) \n
		Returns the data of the spectrum points for transmission from the instrument to the controlling computer. The data can be
		used in MATLAB, for example. Without parameters, the complete waveform is retrieved. Using the offset and length
		parameters, data can be retrieved in smaller portions, which makes the command faster. If you send only one parameter, it
		is interpreted as offset, and the data is retrieved from offset to the end of the waveform. To set the export format, use
		method RsMxo.FormatPy.Data.set. \n
			:param offset: Number of offset waveform points to be skipped.
			:param length: Number of waveform points to be retrieved.
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: spectrum_data: List of values according to the format and content settings."""
		param = ArgSingleList().compose_cmd_string(ArgSingle('offset', offset, DataType.Integer), ArgSingle('length', length, DataType.Integer))
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_bin_or_ascii_float_list(f'FORMAT REAL,32;CALCulate:SPECtrum{spectrum_cmd_val}:WAVeform:MINimum:DATA:VALues? {param}'.rstrip())
		return response
