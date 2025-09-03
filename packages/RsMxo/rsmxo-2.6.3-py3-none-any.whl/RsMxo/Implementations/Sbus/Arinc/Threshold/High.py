from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HighCls:
	"""High commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("high", core, parent)

	def set(self, upper_thresholdhold: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:THReshold:HIGH \n
		Snippet: driver.sbus.arinc.threshold.high.set(upper_thresholdhold = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the upper threshold level of the signal. \n
			:param upper_thresholdhold: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(upper_thresholdhold)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:THReshold:HIGH {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:ARINc:THReshold:HIGH \n
		Snippet: value: float = driver.sbus.arinc.threshold.high.get(serialBus = repcap.SerialBus.Default) \n
		Sets the upper threshold level of the signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: upper_thresholdhold: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:THReshold:HIGH?')
		return Conversions.str_to_float(response)
