from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, frequency: float, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:DISPlay:FREQuency:STOP[:VALue] \n
		Snippet: driver.power.harmonics.display.frequency.stop.value.set(frequency = 1.0, power = repcap.Power.Default) \n
		Sets the stop frequency of the bar graph display. The maximum value is defined by standard and fundamental frequency. \n
			:param frequency: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(frequency)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:DISPlay:FREQuency:STOP:VALue {param}')

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:HARMonics:DISPlay:FREQuency:STOP[:VALue] \n
		Snippet: value: float = driver.power.harmonics.display.frequency.stop.value.get(power = repcap.Power.Default) \n
		Sets the stop frequency of the bar graph display. The maximum value is defined by standard and fundamental frequency. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: frequency: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:DISPlay:FREQuency:STOP:VALue?')
		return Conversions.str_to_float(response)
