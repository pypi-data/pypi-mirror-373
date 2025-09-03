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
		"""POWer<*>:HARMonics:DISPlay:FREQuency:STARt[:VALue] \n
		Snippet: driver.power.harmonics.display.frequency.start.value.set(frequency = 1.0, power = repcap.Power.Default) \n
		Sets the start frequency of a bar graph display. At least three bars are displayed. \n
			:param frequency: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(frequency)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:DISPlay:FREQuency:STARt:VALue {param}')

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:HARMonics:DISPlay:FREQuency:STARt[:VALue] \n
		Snippet: value: float = driver.power.harmonics.display.frequency.start.value.get(power = repcap.Power.Default) \n
		Sets the start frequency of a bar graph display. At least three bars are displayed. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: frequency: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:DISPlay:FREQuency:STARt:VALue?')
		return Conversions.str_to_float(response)
