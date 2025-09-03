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

	def set(self, act_pow_mode: enums.AutoUser, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:RPOWer[:MODE] \n
		Snippet: driver.power.harmonics.rpower.mode.set(act_pow_mode = enums.AutoUser.AUTO, power = repcap.Power.Default) \n
		Available if method RsMxo.Power.Harmonics.Standard.set is set to END. Selects if the power factor is defined
		automatically, or a user-defined value is used (method RsMxo.Power.Harmonics.Rpower.User.set) . \n
			:param act_pow_mode: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(act_pow_mode, enums.AutoUser)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:RPOWer:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.AutoUser:
		"""POWer<*>:HARMonics:RPOWer[:MODE] \n
		Snippet: value: enums.AutoUser = driver.power.harmonics.rpower.mode.get(power = repcap.Power.Default) \n
		Available if method RsMxo.Power.Harmonics.Standard.set is set to END. Selects if the power factor is defined
		automatically, or a user-defined value is used (method RsMxo.Power.Harmonics.Rpower.User.set) . \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: act_pow_mode: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:RPOWer:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoUser)
