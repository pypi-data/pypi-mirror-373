from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CurrentCls:
	"""Current commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("current", core, parent)

	def set(self, source_current: enums.Source, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:SOURce:CURRent \n
		Snippet: driver.power.quality.source.current.set(source_current = enums.Source.C1, power = repcap.Power.Default) \n
		Selects the current source waveform. Active analog channels and math waveforms can be used. \n
			:param source_current: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(source_current, enums.Source)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:SOURce:CURRent {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.Source:
		"""POWer<*>:QUALity:SOURce:CURRent \n
		Snippet: value: enums.Source = driver.power.quality.source.current.get(power = repcap.Power.Default) \n
		Selects the current source waveform. Active analog channels and math waveforms can be used. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: source_current: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:SOURce:CURRent?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
