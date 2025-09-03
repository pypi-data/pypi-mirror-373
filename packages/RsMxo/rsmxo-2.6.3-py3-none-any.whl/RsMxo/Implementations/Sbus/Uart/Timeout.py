from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimeoutCls:
	"""Timeout commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("timeout", core, parent)

	def set(self, timeout: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:TOUT \n
		Snippet: driver.sbus.uart.timeout.set(timeout = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the timeout between packets in a UART data stream. A new packet starts with the first start bit after the timeout.
		The command is relevant if method RsMxo.Sbus.Uart.Packets.set is set to TOUT. \n
			:param timeout: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(timeout)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:TOUT {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:UART:TOUT \n
		Snippet: value: float = driver.sbus.uart.timeout.get(serialBus = repcap.SerialBus.Default) \n
		Sets the timeout between packets in a UART data stream. A new packet starts with the first start bit after the timeout.
		The command is relevant if method RsMxo.Sbus.Uart.Packets.set is set to TOUT. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: timeout: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:TOUT?')
		return Conversions.str_to_float(response)
