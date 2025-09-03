from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UpperCls:
	"""Upper commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("upper", core, parent)

	def set(self, upper_threshold: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:TNOS:THReshold:UPPer \n
		Snippet: driver.sbus.tnos.threshold.upper.set(upper_threshold = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets an upper threshold. \n
			:param upper_threshold: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(upper_threshold)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:TNOS:THReshold:UPPer {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:TNOS:THReshold:UPPer \n
		Snippet: value: float = driver.sbus.tnos.threshold.upper.get(serialBus = repcap.SerialBus.Default) \n
		Sets an upper threshold. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: upper_threshold: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:TNOS:THReshold:UPPer?')
		return Conversions.str_to_float(response)
