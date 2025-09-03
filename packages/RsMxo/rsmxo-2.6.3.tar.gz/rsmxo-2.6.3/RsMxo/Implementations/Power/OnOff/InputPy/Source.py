from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, input_source: enums.Source, power=repcap.Power.Default) -> None:
		"""POWer<*>:ONOFf:INPut[:SOURce] \n
		Snippet: driver.power.onOff.inputPy.source.set(input_source = enums.Source.C1, power = repcap.Power.Default) \n
		Selects the source waveform of the input signal. \n
			:param input_source: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(input_source, enums.Source)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:ONOFf:INPut:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.Source:
		"""POWer<*>:ONOFf:INPut[:SOURce] \n
		Snippet: value: enums.Source = driver.power.onOff.inputPy.source.get(power = repcap.Power.Default) \n
		Selects the source waveform of the input signal. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: input_source: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:INPut:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
