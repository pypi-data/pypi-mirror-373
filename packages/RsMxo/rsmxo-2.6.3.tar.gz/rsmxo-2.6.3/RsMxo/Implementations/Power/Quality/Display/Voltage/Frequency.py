from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def set(self, shw_voltage_freq: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:DISPlay:VOLTage:FREQuency \n
		Snippet: driver.power.quality.display.voltage.frequency.set(shw_voltage_freq = False, power = repcap.Power.Default) \n
		Enables the voltage frequency measurement for the power quality analysis. \n
			:param shw_voltage_freq: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(shw_voltage_freq)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:DISPlay:VOLTage:FREQuency {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>:QUALity:DISPlay:VOLTage:FREQuency \n
		Snippet: value: bool = driver.power.quality.display.voltage.frequency.get(power = repcap.Power.Default) \n
		Enables the voltage frequency measurement for the power quality analysis. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: shw_voltage_freq: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:DISPlay:VOLTage:FREQuency?')
		return Conversions.str_to_bool(response)
