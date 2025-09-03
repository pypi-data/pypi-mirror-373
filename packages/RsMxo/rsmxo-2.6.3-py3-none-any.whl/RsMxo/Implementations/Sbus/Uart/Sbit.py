from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SbitCls:
	"""Sbit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sbit", core, parent)

	def set(self, stop_bits: enums.StopBits, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:SBIT \n
		Snippet: driver.sbus.uart.sbit.set(stop_bits = enums.StopBits.B1, serialBus = repcap.SerialBus.Default) \n
		Sets the number of stop bits: 1 or 1.5 or 2 stop bits are possible. \n
			:param stop_bits: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(stop_bits, enums.StopBits)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:SBIT {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.StopBits:
		"""SBUS<*>:UART:SBIT \n
		Snippet: value: enums.StopBits = driver.sbus.uart.sbit.get(serialBus = repcap.SerialBus.Default) \n
		Sets the number of stop bits: 1 or 1.5 or 2 stop bits are possible. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: stop_bits: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:SBIT?')
		return Conversions.str_to_scalar_enum(response, enums.StopBits)
