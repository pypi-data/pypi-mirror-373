from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, state: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>[:ENABle] \n
		Snippet: driver.power.enable.set(state = False, power = repcap.Power.Default) \n
		Enables the power measurement instance. \n
			:param state: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(state)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:ENABle {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>[:ENABle] \n
		Snippet: value: bool = driver.power.enable.get(power = repcap.Power.Default) \n
		Enables the power measurement instance. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: state: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
