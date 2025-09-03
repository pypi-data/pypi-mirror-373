from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, enab_statistics: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:STATistics[:ENABle] \n
		Snippet: driver.power.quality.statistics.enable.set(enab_statistics = False, power = repcap.Power.Default) \n
		Enables statistical calculation for all power measurements that use statistics. \n
			:param enab_statistics: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(enab_statistics)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:STATistics:ENABle {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>:QUALity:STATistics[:ENABle] \n
		Snippet: value: bool = driver.power.quality.statistics.enable.get(power = repcap.Power.Default) \n
		Enables statistical calculation for all power measurements that use statistics. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: enab_statistics: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:STATistics:ENABle?')
		return Conversions.str_to_bool(response)
