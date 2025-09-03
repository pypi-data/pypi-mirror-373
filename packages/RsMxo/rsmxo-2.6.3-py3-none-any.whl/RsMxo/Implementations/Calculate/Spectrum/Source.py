from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, source: enums.Source, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:SOURce \n
		Snippet: driver.calculate.spectrum.source.set(source = enums.Source.C1, spectrum = repcap.Spectrum.Default) \n
		Selects the source for the spectrum. \n
			:param source: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(source, enums.Source)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.Source:
		"""CALCulate:SPECtrum<*>:SOURce \n
		Snippet: value: enums.Source = driver.calculate.spectrum.source.get(spectrum = repcap.Spectrum.Default) \n
		Selects the source for the spectrum. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: source: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
