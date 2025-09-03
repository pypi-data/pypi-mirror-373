from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LowerCls:
	"""Lower commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lower", core, parent)

	def set(self, lower_threshold: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:TNOS:THReshold:LOWer \n
		Snippet: driver.sbus.tnos.threshold.lower.set(lower_threshold = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets a lower threshold. \n
			:param lower_threshold: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(lower_threshold)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:TNOS:THReshold:LOWer {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:TNOS:THReshold:LOWer \n
		Snippet: value: float = driver.sbus.tnos.threshold.lower.get(serialBus = repcap.SerialBus.Default) \n
		Sets a lower threshold. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: lower_threshold: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:TNOS:THReshold:LOWer?')
		return Conversions.str_to_float(response)
