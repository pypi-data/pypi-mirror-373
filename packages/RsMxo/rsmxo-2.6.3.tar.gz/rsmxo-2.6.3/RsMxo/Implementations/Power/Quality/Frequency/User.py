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

	def set(self, usr_fundam_freq: float, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:FREQuency:USER \n
		Snippet: driver.power.quality.frequency.user.set(usr_fundam_freq = 1.0, power = repcap.Power.Default) \n
		Sets the user-defined frequency, if method RsMxo.Power.Quality.Frequency.Value.set is set to USER. \n
			:param usr_fundam_freq: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(usr_fundam_freq)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:FREQuency:USER {param}')

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:QUALity:FREQuency:USER \n
		Snippet: value: float = driver.power.quality.frequency.user.get(power = repcap.Power.Default) \n
		Sets the user-defined frequency, if method RsMxo.Power.Quality.Frequency.Value.set is set to USER. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: usr_fundam_freq: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:FREQuency:USER?')
		return Conversions.str_to_float(response)
