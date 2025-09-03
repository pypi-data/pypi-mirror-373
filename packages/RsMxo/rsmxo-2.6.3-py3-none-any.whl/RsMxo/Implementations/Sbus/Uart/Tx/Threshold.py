from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThresholdCls:
	"""Threshold commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("threshold", core, parent)

	def set(self, tx_threshold: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:UART:TX:THReshold \n
		Snippet: driver.sbus.uart.tx.threshold.set(tx_threshold = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets a user-defined threshold value for the Tx line. \n
			:param tx_threshold: User-defined clock threshold
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(tx_threshold)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:UART:TX:THReshold {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:UART:TX:THReshold \n
		Snippet: value: float = driver.sbus.uart.tx.threshold.get(serialBus = repcap.SerialBus.Default) \n
		Sets a user-defined threshold value for the Tx line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: tx_threshold: User-defined clock threshold"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:UART:TX:THReshold?')
		return Conversions.str_to_float(response)
