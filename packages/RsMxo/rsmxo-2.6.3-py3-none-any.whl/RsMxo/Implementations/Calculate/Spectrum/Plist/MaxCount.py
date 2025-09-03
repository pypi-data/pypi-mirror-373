from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MaxCountCls:
	"""MaxCount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("maxCount", core, parent)

	def set(self, max_no_ress: int, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:MAXCount \n
		Snippet: driver.calculate.spectrum.plist.maxCount.set(max_no_ress = 1, spectrum = repcap.Spectrum.Default) \n
		Sets the maximum number of measurement results that are listed in the result table. \n
			:param max_no_ress: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.decimal_value_to_str(max_no_ress)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:MAXCount {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> int:
		"""CALCulate:SPECtrum<*>:PLISt:MAXCount \n
		Snippet: value: int = driver.calculate.spectrum.plist.maxCount.get(spectrum = repcap.Spectrum.Default) \n
		Sets the maximum number of measurement results that are listed in the result table. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: max_no_ress: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:MAXCount?')
		return Conversions.str_to_int(response)
