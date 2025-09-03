from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HysteresisCls:
	"""Hysteresis commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hysteresis", core, parent)

	def set(self, tx_hysteresis: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:TX:HYSTeresis \n
		Snippet: driver.sbus.uart.tx.hysteresis.set(tx_hysteresis = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the hysteresis for the TX line. \n
			:param tx_hysteresis: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(tx_hysteresis)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:TX:HYSTeresis {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:UART:TX:HYSTeresis \n
		Snippet: value: float = driver.sbus.uart.tx.hysteresis.get(serialBus = repcap.SerialBus.Default) \n
		Sets the hysteresis for the TX line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: tx_hysteresis: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:TX:HYSTeresis?')
		return Conversions.str_to_float(response)
