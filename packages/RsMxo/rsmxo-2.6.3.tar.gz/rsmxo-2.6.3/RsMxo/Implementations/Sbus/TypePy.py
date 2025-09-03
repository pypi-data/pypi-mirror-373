from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, protocol_type: enums.ProtocolType, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:TYPE \n
		Snippet: driver.sbus.typePy.set(protocol_type = enums.ProtocolType.ARIN429, serialBus = repcap.SerialBus.Default) \n
		Selects the bus type for analysis. The type of buses available depends on the installed options. \n
			:param protocol_type: SPI: SPI protocol, see 'SPI (option R&S MXO5-K510) '. QSPI: Quad SPI protocol, see 'QUAD-SPI (option R&S MXO5-K510) '. I2C: I²C protocol, see 'I²C (option R&S MXO5-K510) '. I3C: I3C protocol, see 'I3C (option R&S MXO5-K550) '. UART: UART protocol, see 'UART / RS-232 (option R&S MXO5- K510) '. CAN: CAN protocol, see 'CAN (option R&S MXO5-K520) '. LIN: LIN protocol, see 'LIN (option R&S MXO5-K520) '. SENT: SENT protocol, see 'SENT (option R&S MXO5-K520) '. ARIN429 | ARINc429: ARINC 429 protocol, see 'ARINC 429 (option R&S MXO5-K530) '. MILS1553 | MILStd: MIL-1553 protocol, see 'MIL-1553 (option R&S MXO5-K530) '. SPMI: SPMI protocol, see 'SPMI (option R&S MXO5-K550) '. RFFE: RFFE protocol, see 'RFFE (option R&S MXO5-K550) '. TNOS: Ethernet 10BASE-T1S protocol, see '10BASE-T1S (option R&S MXO5-K560) '. HBTO: Ethernet 100BASE-T1 protocol, see '100BASE-T1 (option R&S MXO5-K560) '.
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(protocol_type, enums.ProtocolType)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.ProtocolType:
		"""SBUS<*>:TYPE \n
		Snippet: value: enums.ProtocolType = driver.sbus.typePy.get(serialBus = repcap.SerialBus.Default) \n
		Selects the bus type for analysis. The type of buses available depends on the installed options. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: protocol_type: SPI: SPI protocol, see 'SPI (option R&S MXO5-K510) '. QSPI: Quad SPI protocol, see 'QUAD-SPI (option R&S MXO5-K510) '. I2C: I²C protocol, see 'I²C (option R&S MXO5-K510) '. I3C: I3C protocol, see 'I3C (option R&S MXO5-K550) '. UART: UART protocol, see 'UART / RS-232 (option R&S MXO5- K510) '. CAN: CAN protocol, see 'CAN (option R&S MXO5-K520) '. LIN: LIN protocol, see 'LIN (option R&S MXO5-K520) '. SENT: SENT protocol, see 'SENT (option R&S MXO5-K520) '. ARIN429 | ARINc429: ARINC 429 protocol, see 'ARINC 429 (option R&S MXO5-K530) '. MILS1553 | MILStd: MIL-1553 protocol, see 'MIL-1553 (option R&S MXO5-K530) '. SPMI: SPMI protocol, see 'SPMI (option R&S MXO5-K550) '. RFFE: RFFE protocol, see 'RFFE (option R&S MXO5-K550) '. TNOS: Ethernet 10BASE-T1S protocol, see '10BASE-T1S (option R&S MXO5-K560) '. HBTO: Ethernet 100BASE-T1 protocol, see '100BASE-T1 (option R&S MXO5-K560) '."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ProtocolType)
