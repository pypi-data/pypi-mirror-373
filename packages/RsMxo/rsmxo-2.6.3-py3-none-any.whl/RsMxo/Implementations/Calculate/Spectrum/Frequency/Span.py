from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SpanCls:
	"""Span commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("span", core, parent)

	def set(self, span: float, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:FREQuency:SPAN \n
		Snippet: driver.calculate.spectrum.frequency.span.set(span = 1.0, spectrum = repcap.Spectrum.Default) \n
		The span is specified in Hertz and defines the width of the displayed frequency range, which is (Center - Span/2) to
		(Center + Span/2) . The position of the span is defined using the Center setting. \n
			:param span: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(span)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:SPAN {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> float:
		"""CALCulate:SPECtrum<*>:FREQuency:SPAN \n
		Snippet: value: float = driver.calculate.spectrum.frequency.span.get(spectrum = repcap.Spectrum.Default) \n
		The span is specified in Hertz and defines the width of the displayed frequency range, which is (Center - Span/2) to
		(Center + Span/2) . The position of the span is defined using the Center setting. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: span: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:SPAN?')
		return Conversions.str_to_float(response)
