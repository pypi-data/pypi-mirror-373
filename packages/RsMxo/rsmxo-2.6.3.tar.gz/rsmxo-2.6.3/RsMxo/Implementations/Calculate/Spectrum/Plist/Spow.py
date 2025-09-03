from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SpowCls:
	"""Spow commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("spow", core, parent)

	def set(self, shw_peaks_on_wfm: bool, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:SPOW \n
		Snippet: driver.calculate.spectrum.plist.spow.set(shw_peaks_on_wfm = False, spectrum = repcap.Spectrum.Default) \n
		Displays a box with a description for each detected peak in the spectrum, including the magnitude. If method RsMxo.
		Calculate.Spectrum.Plist.Label.Frequency.State.set is ON, the frequency values are also displayed. \n
			:param shw_peaks_on_wfm: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.bool_to_str(shw_peaks_on_wfm)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SPOW {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> bool:
		"""CALCulate:SPECtrum<*>:PLISt:SPOW \n
		Snippet: value: bool = driver.calculate.spectrum.plist.spow.get(spectrum = repcap.Spectrum.Default) \n
		Displays a box with a description for each detected peak in the spectrum, including the magnitude. If method RsMxo.
		Calculate.Spectrum.Plist.Label.Frequency.State.set is ON, the frequency values are also displayed. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: shw_peaks_on_wfm: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SPOW?')
		return Conversions.str_to_bool(response)
