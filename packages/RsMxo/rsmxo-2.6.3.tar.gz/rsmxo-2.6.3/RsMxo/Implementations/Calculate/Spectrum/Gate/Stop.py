from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StopCls:
	"""Stop commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stop", core, parent)

	def set(self, stop: float, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:GATE:STOP \n
		Snippet: driver.calculate.spectrum.gate.stop.set(stop = 1.0, spectrum = repcap.Spectrum.Default) \n
		Sets the end value for the gate. \n
			:param stop: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(stop)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:GATE:STOP {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> float:
		"""CALCulate:SPECtrum<*>:GATE:STOP \n
		Snippet: value: float = driver.calculate.spectrum.gate.stop.get(spectrum = repcap.Spectrum.Default) \n
		Sets the end value for the gate. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: stop: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:GATE:STOP?')
		return Conversions.str_to_float(response)
