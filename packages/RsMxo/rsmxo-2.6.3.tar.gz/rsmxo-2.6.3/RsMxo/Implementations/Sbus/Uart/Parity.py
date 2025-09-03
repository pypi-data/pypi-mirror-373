from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ParityCls:
	"""Parity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("parity", core, parent)

	def set(self, parity: enums.SbusUartParity, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:PARity \n
		Snippet: driver.sbus.uart.parity.set(parity = enums.SbusUartParity.DC, serialBus = repcap.SerialBus.Default) \n
		Defines the optional parity bit that is used for error detection. \n
			:param parity:
				- MARK: The parity bit is always a logic 1.
				- SPC: SPaCe: The parity bit is always a logic 0.
				- DC: Do not care: the parity is ignored.
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')"""
		param = Conversions.enum_scalar_to_str(parity, enums.SbusUartParity)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:PARity {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusUartParity:
		"""SBUS<*>:UART:PARity \n
		Snippet: value: enums.SbusUartParity = driver.sbus.uart.parity.get(serialBus = repcap.SerialBus.Default) \n
		Defines the optional parity bit that is used for error detection. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: parity:
				- MARK: The parity bit is always a logic 1.
				- SPC: SPaCe: The parity bit is always a logic 0.
				- DC: Do not care: the parity is ignored."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:PARity?')
		return Conversions.str_to_scalar_enum(response, enums.SbusUartParity)
