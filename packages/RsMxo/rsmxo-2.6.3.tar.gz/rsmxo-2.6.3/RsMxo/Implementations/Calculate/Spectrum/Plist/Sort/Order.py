from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OrderCls:
	"""Order commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("order", core, parent)

	def set(self, result_order: enums.ResultOrder, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:SORT:ORDer \n
		Snippet: driver.calculate.spectrum.plist.sort.order.set(result_order = enums.ResultOrder.ASC, spectrum = repcap.Spectrum.Default) \n
		Defines if the spectrum peak list results are sorted in an ascending (increasing) or descending (decreasing) order. \n
			:param result_order: ASC: ascending DESC: descending
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(result_order, enums.ResultOrder)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SORT:ORDer {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.ResultOrder:
		"""CALCulate:SPECtrum<*>:PLISt:SORT:ORDer \n
		Snippet: value: enums.ResultOrder = driver.calculate.spectrum.plist.sort.order.get(spectrum = repcap.Spectrum.Default) \n
		Defines if the spectrum peak list results are sorted in an ascending (increasing) or descending (decreasing) order. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: result_order: ASC: ascending DESC: descending"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SORT:ORDer?')
		return Conversions.str_to_scalar_enum(response, enums.ResultOrder)
