from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PexcursionCls:
	"""Pexcursion commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pexcursion", core, parent)

	def set(self, peak_excursion: float, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PEXCursion \n
		Snippet: driver.calculate.spectrum.pexcursion.set(peak_excursion = 1.0, spectrum = repcap.Spectrum.Default) \n
		Defines a minimum level value by which the waveform must drop left and right of the local maximum to be listed as a peak.
		Enter a peak excursion value to omit close by peaks and list just the highest peak. \n
			:param peak_excursion: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(peak_excursion)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PEXCursion {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> float:
		"""CALCulate:SPECtrum<*>:PEXCursion \n
		Snippet: value: float = driver.calculate.spectrum.pexcursion.get(spectrum = repcap.Spectrum.Default) \n
		Defines a minimum level value by which the waveform must drop left and right of the local maximum to be listed as a peak.
		Enter a peak excursion value to omit close by peaks and list just the highest peak. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: peak_excursion: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PEXCursion?')
		return Conversions.str_to_float(response)
