from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThresholdCls:
	"""Threshold commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("threshold", core, parent)

	def set(self, threshold: float, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:THReshold \n
		Snippet: driver.calculate.spectrum.threshold.set(threshold = 1.0, spectrum = repcap.Spectrum.Default) \n
		Sets an absolute threshold as an additional condition for the peak search. Only peaks that exceed the threshold are
		detected. \n
			:param threshold: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(threshold)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:THReshold {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> float:
		"""CALCulate:SPECtrum<*>:THReshold \n
		Snippet: value: float = driver.calculate.spectrum.threshold.get(spectrum = repcap.Spectrum.Default) \n
		Sets an absolute threshold as an additional condition for the peak search. Only peaks that exceed the threshold are
		detected. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: threshold: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:THReshold?')
		return Conversions.str_to_float(response)
