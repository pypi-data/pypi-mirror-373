from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, window_function: enums.WindowFunction, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:FREQuency:WINDow:TYPE \n
		Snippet: driver.calculate.spectrum.frequency.window.typePy.set(window_function = enums.WindowFunction.BLACkharris, spectrum = repcap.Spectrum.Default) \n
		Selects the window type. Windowing helps minimize the discontinuities at the end of the measured signal interval and thus
		reduces the effect of spectral leakage, increasing the frequency resolution. Various different window functions are
		provided in the MXO 5 to suit different input signals. Each of the window functions has specific characteristics,
		including some advantages and some trade-offs. Consider these characteristics carefully to find the optimum solution for
		the measurement task. \n
			:param window_function:
				- RECTangular: The rectangular window has the best frequency resolution, but a poor amplitude accuracy and is recommended for separating two tones with almost equal amplitudes and a small frequency distance.
				- HAMMing: The Hamming window is bell shaped and has a good frequency resolution and fair amplitude accuracy. It is recommended for frequency response measurements and sine waves, periodic signals and narrowband noise.
				- HANN: The Hann window is bell shaped and has a slightly worse frequency resolution but smaller sidelobe level than the Hamming window. The applications are the same.
				- BLACkharris: The Blackman window is bell shaped and has a poor frequency resolution, but very good amplitude accuracy. It is recommended mainly for signals with single frequencies to detect harmonics.
				- GAUSsian: Good frequency resolution and best magnitude resolution, recommended for weak signals and short duration
				- FLATtop2 | FLATTOP2: The flat top window has a poor frequency resolution, but the best amplitude accuracy and the sharpest sidelobe. It is recommended for accurate single tone amplitude measurements.
				- KAISerbessel: The kaiser-bessel window has a fair frequency resolution and good amplitude accuracy, and a very high sidelobe level. It is recommended for separating two tones with differing amplitudes and a small frequency distance.
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')"""
		param = Conversions.enum_scalar_to_str(window_function, enums.WindowFunction)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:WINDow:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.WindowFunction:
		"""CALCulate:SPECtrum<*>:FREQuency:WINDow:TYPE \n
		Snippet: value: enums.WindowFunction = driver.calculate.spectrum.frequency.window.typePy.get(spectrum = repcap.Spectrum.Default) \n
		Selects the window type. Windowing helps minimize the discontinuities at the end of the measured signal interval and thus
		reduces the effect of spectral leakage, increasing the frequency resolution. Various different window functions are
		provided in the MXO 5 to suit different input signals. Each of the window functions has specific characteristics,
		including some advantages and some trade-offs. Consider these characteristics carefully to find the optimum solution for
		the measurement task. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: window_function:
				- RECTangular: The rectangular window has the best frequency resolution, but a poor amplitude accuracy and is recommended for separating two tones with almost equal amplitudes and a small frequency distance.
				- HAMMing: The Hamming window is bell shaped and has a good frequency resolution and fair amplitude accuracy. It is recommended for frequency response measurements and sine waves, periodic signals and narrowband noise.
				- HANN: The Hann window is bell shaped and has a slightly worse frequency resolution but smaller sidelobe level than the Hamming window. The applications are the same.
				- BLACkharris: The Blackman window is bell shaped and has a poor frequency resolution, but very good amplitude accuracy. It is recommended mainly for signals with single frequencies to detect harmonics.
				- GAUSsian: Good frequency resolution and best magnitude resolution, recommended for weak signals and short duration
				- FLATtop2 | FLATTOP2: The flat top window has a poor frequency resolution, but the best amplitude accuracy and the sharpest sidelobe. It is recommended for accurate single tone amplitude measurements.
				- KAISerbessel: The kaiser-bessel window has a fair frequency resolution and good amplitude accuracy, and a very high sidelobe level. It is recommended for separating two tones with differing amplitudes and a small frequency distance."""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:WINDow:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.WindowFunction)
