from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, fundam_freq: enums.PqualFundamentalFreq, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:FREQuency[:VALue] \n
		Snippet: driver.power.quality.frequency.value.set(fundam_freq = enums.PqualFundamentalFreq.AUTO, power = repcap.Power.Default) \n
		Sets the input frequency of the source signal in Hz. \n
			:param fundam_freq: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(fundam_freq, enums.PqualFundamentalFreq)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:FREQuency:VALue {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.PqualFundamentalFreq:
		"""POWer<*>:QUALity:FREQuency[:VALue] \n
		Snippet: value: enums.PqualFundamentalFreq = driver.power.quality.frequency.value.get(power = repcap.Power.Default) \n
		Sets the input frequency of the source signal in Hz. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: fundam_freq: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:FREQuency:VALue?')
		return Conversions.str_to_scalar_enum(response, enums.PqualFundamentalFreq)
