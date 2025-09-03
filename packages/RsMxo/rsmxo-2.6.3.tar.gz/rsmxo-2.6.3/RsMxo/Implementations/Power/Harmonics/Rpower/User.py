from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UserCls:
	"""User commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("user", core, parent)

	def set(self, user_act_power: float, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:RPOWer:USER \n
		Snippet: driver.power.harmonics.rpower.user.set(user_act_power = 1.0, power = repcap.Power.Default) \n
		Selects the revision of the EN61000 standard, if method RsMxo.Power.Harmonics.Standard.set is set to END and method RsMxo.
		Power.Harmonics.Rpower.User.set is set to USER. Sets a user-defined power value. \n
			:param user_act_power: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(user_act_power)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:RPOWer:USER {param}')

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:HARMonics:RPOWer:USER \n
		Snippet: value: float = driver.power.harmonics.rpower.user.get(power = repcap.Power.Default) \n
		Selects the revision of the EN61000 standard, if method RsMxo.Power.Harmonics.Standard.set is set to END and method RsMxo.
		Power.Harmonics.Rpower.User.set is set to USER. Sets a user-defined power value. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: user_act_power: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:RPOWer:USER?')
		return Conversions.str_to_float(response)
