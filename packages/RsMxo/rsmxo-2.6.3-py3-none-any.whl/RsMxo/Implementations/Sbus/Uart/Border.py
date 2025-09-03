from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BorderCls:
	"""Border commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("border", core, parent)

	def set(self, bit_order: enums.BitOrder, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:BORDer \n
		Snippet: driver.sbus.uart.border.set(bit_order = enums.BitOrder.LSBF, serialBus = repcap.SerialBus.Default) \n
		Selects the bit order, which determines if the data of the messages starts with MSB (most significant bit) or LSB (least
		significant bit) . \n
			:param bit_order: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(bit_order, enums.BitOrder)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:BORDer {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.BitOrder:
		"""SBUS<*>:UART:BORDer \n
		Snippet: value: enums.BitOrder = driver.sbus.uart.border.get(serialBus = repcap.SerialBus.Default) \n
		Selects the bit order, which determines if the data of the messages starts with MSB (most significant bit) or LSB (least
		significant bit) . \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: bit_order: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:BORDer?')
		return Conversions.str_to_scalar_enum(response, enums.BitOrder)
