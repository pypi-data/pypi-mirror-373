from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, pow_factor_mode: enums.AutoUser, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:PFACtor[:MODE] \n
		Snippet: driver.power.harmonics.pfactor.mode.set(pow_factor_mode = enums.AutoUser.AUTO, power = repcap.Power.Default) \n
		Available if method RsMxo.Power.Harmonics.Standard.set is set to ENC. Selects if the power factor is defined
		automatically, or a user-defined value is used (method RsMxo.Power.Harmonics.Pfactor.User.set) . \n
			:param pow_factor_mode: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(pow_factor_mode, enums.AutoUser)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:PFACtor:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.AutoUser:
		"""POWer<*>:HARMonics:PFACtor[:MODE] \n
		Snippet: value: enums.AutoUser = driver.power.harmonics.pfactor.mode.get(power = repcap.Power.Default) \n
		Available if method RsMxo.Power.Harmonics.Standard.set is set to ENC. Selects if the power factor is defined
		automatically, or a user-defined value is used (method RsMxo.Power.Harmonics.Pfactor.User.set) . \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: pow_factor_mode: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:PFACtor:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoUser)
