from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RatioCls:
	"""Ratio commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ratio", core, parent)

	def set(self, span_rbw_ratio: int, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:FREQuency:BANDwidth[:RESolution]:RATio \n
		Snippet: driver.calculate.spectrum.frequency.bandwidth.resolution.ratio.set(span_rbw_ratio = 1, spectrum = repcap.Spectrum.Default) \n
		Defines the coupling ratio for Span/RBW. Available, if method RsMxo.Calculate.Spectrum.Frequency.Bandwidth.Resolution.
		Auto.set is set to ON. \n
			:param span_rbw_ratio: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(span_rbw_ratio)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:BANDwidth:RESolution:RATio {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> int:
		"""CALCulate:SPECtrum<*>:FREQuency:BANDwidth[:RESolution]:RATio \n
		Snippet: value: int = driver.calculate.spectrum.frequency.bandwidth.resolution.ratio.get(spectrum = repcap.Spectrum.Default) \n
		Defines the coupling ratio for Span/RBW. Available, if method RsMxo.Calculate.Spectrum.Frequency.Bandwidth.Resolution.
		Auto.set is set to ON. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: span_rbw_ratio: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:BANDwidth:RESolution:RATio?')
		return Conversions.str_to_int(response)
