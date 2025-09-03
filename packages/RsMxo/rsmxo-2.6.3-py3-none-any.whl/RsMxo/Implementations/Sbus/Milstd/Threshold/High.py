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

	def set(self, threshold_high: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:MILStd:THReshold:HIGH \n
		Snippet: driver.sbus.milstd.threshold.high.set(threshold_high = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the lower threshold level of the signal. \n
			:param threshold_high: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(threshold_high)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:MILStd:THReshold:HIGH {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:MILStd:THReshold:HIGH \n
		Snippet: value: float = driver.sbus.milstd.threshold.high.get(serialBus = repcap.SerialBus.Default) \n
		Sets the lower threshold level of the signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: threshold_high: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:MILStd:THReshold:HIGH?')
		return Conversions.str_to_float(response)
