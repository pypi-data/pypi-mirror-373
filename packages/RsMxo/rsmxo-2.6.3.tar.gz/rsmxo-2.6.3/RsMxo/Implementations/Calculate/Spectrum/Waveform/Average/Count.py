from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def set(self, average_count: int, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:WAVeform:AVERage:COUNt \n
		Snippet: driver.calculate.spectrum.waveform.average.count.set(average_count = 1, spectrum = repcap.Spectrum.Default) \n
		Sets the number of segments used for the averaging of the spectrum. \n
			:param average_count: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(average_count)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:WAVeform:AVERage:COUNt {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> int:
		"""CALCulate:SPECtrum<*>:WAVeform:AVERage:COUNt \n
		Snippet: value: int = driver.calculate.spectrum.waveform.average.count.get(spectrum = repcap.Spectrum.Default) \n
		Sets the number of segments used for the averaging of the spectrum. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: average_count: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:WAVeform:AVERage:COUNt?')
		return Conversions.str_to_int(response)
