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

	def set(self, pll_order: enums.PllOrder, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:PLL:ORDer \n
		Snippet: driver.treference.cdr.software.pll.order.set(pll_order = enums.PllOrder.FIRSt, timingReference = repcap.TimingReference.Default) \n
		Sets the order of the PLL: first or second order. PLL of higher order can compensate for more complex jitter behavior. \n
			:param pll_order: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.enum_scalar_to_str(pll_order, enums.PllOrder)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:PLL:ORDer {param}')

	# noinspection PyTypeChecker
	def get(self, timingReference=repcap.TimingReference.Default) -> enums.PllOrder:
		"""TREFerence<*>:CDR:SOFTware:PLL:ORDer \n
		Snippet: value: enums.PllOrder = driver.treference.cdr.software.pll.order.get(timingReference = repcap.TimingReference.Default) \n
		Sets the order of the PLL: first or second order. PLL of higher order can compensate for more complex jitter behavior. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: pll_order: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:PLL:ORDer?')
		return Conversions.str_to_scalar_enum(response, enums.PllOrder)
