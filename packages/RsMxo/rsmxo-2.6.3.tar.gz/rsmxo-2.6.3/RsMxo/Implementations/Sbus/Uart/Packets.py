from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PacketsCls:
	"""Packets commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("packets", core, parent)

	def set(self, frm_separation: enums.SbusUartFrameSeparation, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:PACKets \n
		Snippet: driver.sbus.uart.packets.set(frm_separation = enums.SbusUartFrameSeparation.NONE, serialBus = repcap.SerialBus.Default) \n
		Defines the method of packet separation. A packet is a number of subsequent words in a date stream. \n
			:param frm_separation:
				- NONE: Packets are not considered.
				- EWORd: End word, the end condition of a packet is a pattern. To define the end word, use SBUSsb:UART:EWORd.
				- TOUT: Defines a timeout between the packets. To set the timeout, use SBUSsb:UART:TOUT.
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')"""
		param = Conversions.enum_scalar_to_str(frm_separation, enums.SbusUartFrameSeparation)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:PACKets {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusUartFrameSeparation:
		"""SBUS<*>:UART:PACKets \n
		Snippet: value: enums.SbusUartFrameSeparation = driver.sbus.uart.packets.get(serialBus = repcap.SerialBus.Default) \n
		Defines the method of packet separation. A packet is a number of subsequent words in a date stream. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: frm_separation:
				- NONE: Packets are not considered.
				- EWORd: End word, the end condition of a packet is a pattern. To define the end word, use SBUSsb:UART:EWORd.
				- TOUT: Defines a timeout between the packets. To set the timeout, use SBUSsb:UART:TOUT."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:PACKets?')
		return Conversions.str_to_scalar_enum(response, enums.SbusUartFrameSeparation)
