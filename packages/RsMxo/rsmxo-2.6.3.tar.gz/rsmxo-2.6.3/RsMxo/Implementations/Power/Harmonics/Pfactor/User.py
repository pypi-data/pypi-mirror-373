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

	def set(self, user_power_factor: float, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:PFACtor:USER \n
		Snippet: driver.power.harmonics.pfactor.user.set(user_power_factor = 1.0, power = repcap.Power.Default) \n
		Available if method RsMxo.Power.Harmonics.Standard.set is set to ENC and method RsMxo.Power.Harmonics.Pfactor.Mode.set is
		set to USER. Sets a user-defined power factor. \n
			:param user_power_factor: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(user_power_factor)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:PFACtor:USER {param}')

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:HARMonics:PFACtor:USER \n
		Snippet: value: float = driver.power.harmonics.pfactor.user.get(power = repcap.Power.Default) \n
		Available if method RsMxo.Power.Harmonics.Standard.set is set to ENC and method RsMxo.Power.Harmonics.Pfactor.Mode.set is
		set to USER. Sets a user-defined power factor. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: user_power_factor: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:PFACtor:USER?')
		return Conversions.str_to_float(response)
