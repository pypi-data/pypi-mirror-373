from typing import List

from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValuesCls:
	"""Values commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("values", core, parent)

	def get(self, spectrum=repcap.Spectrum.Default) -> List[float]:
		"""CALCulate:SPECtrum<*>:WAVeform:MAXimum:DATA[:VALues] \n
		Snippet: value: List[float] = driver.calculate.spectrum.waveform.maximum.data.values.get(spectrum = repcap.Spectrum.Default) \n
		Returns the data of the spectrum points for transmission from the instrument to the controlling computer. The data can be
		used in MATLAB, for example. Without parameters, the complete waveform is retrieved. Using the offset and length
		parameters, data can be retrieved in smaller portions, which makes the command faster. If you send only one parameter, it
		is interpreted as offset, and the data is retrieved from offset to the end of the waveform. To set the export format, use
		method RsMxo.FormatPy.Data.set. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: spectrum_data: List of values according to the format and content settings."""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_bin_or_ascii_float_list(f'FORMAT REAL,32;CALCulate:SPECtrum{spectrum_cmd_val}:WAVeform:MAXimum:DATA:VALues?')
		return response
