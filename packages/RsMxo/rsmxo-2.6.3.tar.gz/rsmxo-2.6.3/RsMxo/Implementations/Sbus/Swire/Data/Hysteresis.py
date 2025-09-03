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

	def set(self, data_hysteresis: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SWIRe:DATA:HYSTeresis \n
		Snippet: driver.sbus.swire.data.hysteresis.set(data_hysteresis = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the hysteresis for the data channel. \n
			:param data_hysteresis: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(data_hysteresis)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SWIRe:DATA:HYSTeresis {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:SWIRe:DATA:HYSTeresis \n
		Snippet: value: float = driver.sbus.swire.data.hysteresis.get(serialBus = repcap.SerialBus.Default) \n
		Sets the hysteresis for the data channel. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data_hysteresis: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SWIRe:DATA:HYSTeresis?')
		return Conversions.str_to_float(response)
