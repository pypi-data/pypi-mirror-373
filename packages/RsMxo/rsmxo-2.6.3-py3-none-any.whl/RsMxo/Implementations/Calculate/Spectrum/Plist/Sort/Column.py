from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ColumnCls:
	"""Column commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("column", core, parent)

	def set(self, result_column: enums.ResultColumn, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:SORT:COLumn \n
		Snippet: driver.calculate.spectrum.plist.sort.column.set(result_column = enums.ResultColumn.FREQ, spectrum = repcap.Spectrum.Default) \n
		Sorts the results in the spectrum peak list table either according to the frequency or according to the value. \n
			:param result_column: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(result_column, enums.ResultColumn)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SORT:COLumn {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.ResultColumn:
		"""CALCulate:SPECtrum<*>:PLISt:SORT:COLumn \n
		Snippet: value: enums.ResultColumn = driver.calculate.spectrum.plist.sort.column.get(spectrum = repcap.Spectrum.Default) \n
		Sorts the results in the spectrum peak list table either according to the frequency or according to the value. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: result_column: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SORT:COLumn?')
		return Conversions.str_to_scalar_enum(response, enums.ResultColumn)
