from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BitrateCls:
	"""Bitrate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bitrate", core, parent)

	def set(self, bitrate: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:BITRate \n
		Snippet: driver.sbus.uart.bitrate.set(bitrate = 1, serialBus = repcap.SerialBus.Default) \n
		Sets the number of transmitted bits per second. \n
			:param bitrate: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(bitrate)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:BITRate {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:UART:BITRate \n
		Snippet: value: int = driver.sbus.uart.bitrate.get(serialBus = repcap.SerialBus.Default) \n
		Sets the number of transmitted bits per second. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: bitrate: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:BITRate?')
		return Conversions.str_to_int(response)
