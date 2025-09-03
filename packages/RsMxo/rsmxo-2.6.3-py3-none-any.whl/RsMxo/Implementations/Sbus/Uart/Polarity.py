from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PolarityCls:
	"""Polarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polarity", core, parent)

	def set(self, polarity: enums.SbusLinUartPolarity, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:POLarity \n
		Snippet: driver.sbus.uart.polarity.set(polarity = enums.SbusLinUartPolarity.IDLHigh, serialBus = repcap.SerialBus.Default) \n
		Defines the logic levels of the bus. The idle state corresponds to a logic 1. The start bit corresponds to a logic 0.
		Idle high (high=1) is used, for example, for control signals, while Idle low (low=1) is defined for data lines (RS-232) . \n
			:param polarity: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(polarity, enums.SbusLinUartPolarity)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusLinUartPolarity:
		"""SBUS<*>:UART:POLarity \n
		Snippet: value: enums.SbusLinUartPolarity = driver.sbus.uart.polarity.get(serialBus = repcap.SerialBus.Default) \n
		Defines the logic levels of the bus. The idle state corresponds to a logic 1. The start bit corresponds to a logic 0.
		Idle high (high=1) is used, for example, for control signals, while Idle low (low=1) is defined for data lines (RS-232) . \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: polarity: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.SbusLinUartPolarity)
