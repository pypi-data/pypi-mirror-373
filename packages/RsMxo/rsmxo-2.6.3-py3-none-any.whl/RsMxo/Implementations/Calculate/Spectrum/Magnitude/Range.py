from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RangeCls:
	"""Range commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("range", core, parent)

	def set(self, vertical_range: float, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:MAGNitude:RANGe \n
		Snippet: driver.calculate.spectrum.magnitude.range.set(vertical_range = 1.0, spectrum = repcap.Spectrum.Default) \n
		Sets the range of the spectrum values to be displayed. \n
			:param vertical_range: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(vertical_range)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:MAGNitude:RANGe {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> float:
		"""CALCulate:SPECtrum<*>:MAGNitude:RANGe \n
		Snippet: value: float = driver.calculate.spectrum.magnitude.range.get(spectrum = repcap.Spectrum.Default) \n
		Sets the range of the spectrum values to be displayed. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: vertical_range: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:MAGNitude:RANGe?')
		return Conversions.str_to_float(response)
