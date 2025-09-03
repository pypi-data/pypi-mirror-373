from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class InvertCls:
	"""Invert commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("invert", core, parent)

	def set(self, inverse: bool, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:LABel:INVert \n
		Snippet: driver.calculate.spectrum.plist.label.invert.set(inverse = False, spectrum = repcap.Spectrum.Default) \n
		Inverts the colors of the peak list labels, the peak boxes are shown with a white background. \n
			:param inverse: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.bool_to_str(inverse)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:LABel:INVert {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> bool:
		"""CALCulate:SPECtrum<*>:PLISt:LABel:INVert \n
		Snippet: value: bool = driver.calculate.spectrum.plist.label.invert.get(spectrum = repcap.Spectrum.Default) \n
		Inverts the colors of the peak list labels, the peak boxes are shown with a white background. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: inverse: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:LABel:INVert?')
		return Conversions.str_to_bool(response)
