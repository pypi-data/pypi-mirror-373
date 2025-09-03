from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, result_mode: enums.AbsRel, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:MODE \n
		Snippet: driver.calculate.spectrum.plist.mode.set(result_mode = enums.AbsRel.ABS, spectrum = repcap.Spectrum.Default) \n
		Selects how the measurement results are displayed. \n
			:param result_mode: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(result_mode, enums.AbsRel)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.AbsRel:
		"""CALCulate:SPECtrum<*>:PLISt:MODE \n
		Snippet: value: enums.AbsRel = driver.calculate.spectrum.plist.mode.get(spectrum = repcap.Spectrum.Default) \n
		Selects how the measurement results are displayed. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: result_mode: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AbsRel)
