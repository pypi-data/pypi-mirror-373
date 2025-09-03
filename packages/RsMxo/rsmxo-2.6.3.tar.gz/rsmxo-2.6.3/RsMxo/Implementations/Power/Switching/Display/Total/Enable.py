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

	def set(self, show_total: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>:SWITching:DISPlay:TOTal[:ENABle] \n
		Snippet: driver.power.switching.display.total.enable.set(show_total = False, power = repcap.Power.Default) \n
		Enables the measurements of the total switching cycle. \n
			:param show_total: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(show_total)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:SWITching:DISPlay:TOTal:ENABle {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>:SWITching:DISPlay:TOTal[:ENABle] \n
		Snippet: value: bool = driver.power.switching.display.total.enable.get(power = repcap.Power.Default) \n
		Enables the measurements of the total switching cycle. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: show_total: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:DISPlay:TOTal:ENABle?')
		return Conversions.str_to_bool(response)
