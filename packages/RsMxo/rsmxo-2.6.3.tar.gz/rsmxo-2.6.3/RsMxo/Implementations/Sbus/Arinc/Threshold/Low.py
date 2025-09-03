from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LowCls:
	"""Low commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("low", core, parent)

	def set(self, lower_thresholdhold: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:THReshold:LOW \n
		Snippet: driver.sbus.arinc.threshold.low.set(lower_thresholdhold = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the lower threshold level of the signal. \n
			:param lower_thresholdhold: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(lower_thresholdhold)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:THReshold:LOW {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:ARINc:THReshold:LOW \n
		Snippet: value: float = driver.sbus.arinc.threshold.low.get(serialBus = repcap.SerialBus.Default) \n
		Sets the lower threshold level of the signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: lower_thresholdhold: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:THReshold:LOW?')
		return Conversions.str_to_float(response)
