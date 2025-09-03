from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CenterCls:
	"""Center commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("center", core, parent)

	def set(self, center: float, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:FREQuency:CENTer \n
		Snippet: driver.calculate.spectrum.frequency.center.set(center = 1.0, spectrum = repcap.Spectrum.Default) \n
		Defines the position of the displayed frequency range, which is (Center - Span/2) to (Center + Span/2) . The width of the
		range is defined using the frequency span setting. \n
			:param center: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(center)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:CENTer {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> float:
		"""CALCulate:SPECtrum<*>:FREQuency:CENTer \n
		Snippet: value: float = driver.calculate.spectrum.frequency.center.get(spectrum = repcap.Spectrum.Default) \n
		Defines the position of the displayed frequency range, which is (Center - Span/2) to (Center + Span/2) . The width of the
		range is defined using the frequency span setting. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: center: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:CENTer?')
		return Conversions.str_to_float(response)
