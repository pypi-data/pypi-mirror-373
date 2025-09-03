from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, show_non_conduction: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>:SWITching:DISPlay:NCONduction[:ENABle] \n
		Snippet: driver.power.switching.display.nconduction.enable.set(show_non_conduction = False, power = repcap.Power.Default) \n
		The commands enable the measurements of the conduction area, non-conduction area, turn off area and turn on area,
		respectively. Results of enabled mesurements are shown in the result table. \n
			:param show_non_conduction: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(show_non_conduction)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:SWITching:DISPlay:NCONduction:ENABle {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>:SWITching:DISPlay:NCONduction[:ENABle] \n
		Snippet: value: bool = driver.power.switching.display.nconduction.enable.get(power = repcap.Power.Default) \n
		The commands enable the measurements of the conduction area, non-conduction area, turn off area and turn on area,
		respectively. Results of enabled mesurements are shown in the result table. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: show_non_conduction: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:DISPlay:NCONduction:ENABle?')
		return Conversions.str_to_bool(response)
