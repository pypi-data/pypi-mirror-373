from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, show_frequency: bool, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:LABel:FREQuency[:STATe] \n
		Snippet: driver.calculate.spectrum.plist.label.frequency.state.set(show_frequency = False, spectrum = repcap.Spectrum.Default) \n
		Includes the frequency of the detected peak in the diagram labels. \n
			:param show_frequency: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.bool_to_str(show_frequency)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:LABel:FREQuency:STATe {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> bool:
		"""CALCulate:SPECtrum<*>:PLISt:LABel:FREQuency[:STATe] \n
		Snippet: value: bool = driver.calculate.spectrum.plist.label.frequency.state.get(spectrum = repcap.Spectrum.Default) \n
		Includes the frequency of the detected peak in the diagram labels. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: show_frequency: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:LABel:FREQuency:STATe?')
		return Conversions.str_to_bool(response)
