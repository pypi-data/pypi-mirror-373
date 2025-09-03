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

	def set(self, data_threshold: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:RFFE:DATA:THReshold \n
		Snippet: driver.sbus.rffe.data.threshold.set(data_threshold = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets a threshold value for the data line. \n
			:param data_threshold: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(data_threshold)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:RFFE:DATA:THReshold {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:RFFE:DATA:THReshold \n
		Snippet: value: float = driver.sbus.rffe.data.threshold.get(serialBus = repcap.SerialBus.Default) \n
		Sets a threshold value for the data line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data_threshold: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RFFE:DATA:THReshold?')
		return Conversions.str_to_float(response)
