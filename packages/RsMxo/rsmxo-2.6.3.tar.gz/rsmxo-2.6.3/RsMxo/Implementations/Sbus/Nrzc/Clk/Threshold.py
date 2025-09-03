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

	def set(self, clk_threshold: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZC:CLK:THReshold \n
		Snippet: driver.sbus.nrzc.clk.threshold.set(clk_threshold = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the threshold value for the digitization of the clock signal. \n
			:param clk_threshold: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(clk_threshold)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:CLK:THReshold {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:NRZC:CLK:THReshold \n
		Snippet: value: float = driver.sbus.nrzc.clk.threshold.get(serialBus = repcap.SerialBus.Default) \n
		Sets the threshold value for the digitization of the clock signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: clk_threshold: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:CLK:THReshold?')
		return Conversions.str_to_float(response)
