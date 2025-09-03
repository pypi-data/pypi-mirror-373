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

	def set(self, threshold_low: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:MILStd:THReshold:LOW \n
		Snippet: driver.sbus.milstd.threshold.low.set(threshold_low = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the lower threshold level of the signal. \n
			:param threshold_low: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(threshold_low)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:MILStd:THReshold:LOW {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:MILStd:THReshold:LOW \n
		Snippet: value: float = driver.sbus.milstd.threshold.low.get(serialBus = repcap.SerialBus.Default) \n
		Sets the lower threshold level of the signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: threshold_low: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:MILStd:THReshold:LOW?')
		return Conversions.str_to_float(response)
