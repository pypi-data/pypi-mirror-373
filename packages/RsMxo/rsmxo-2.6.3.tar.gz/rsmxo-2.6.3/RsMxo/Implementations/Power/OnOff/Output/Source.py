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

	def set(self, output_source: enums.Source, power=repcap.Power.Default, output=repcap.Output.Default) -> None:
		"""POWer<*>:ONOFf:OUTPut<*>[:SOURce] \n
		Snippet: driver.power.onOff.output.source.set(output_source = enums.Source.C1, power = repcap.Power.Default, output = repcap.Output.Default) \n
		Selects the channel of the output signal. All analog channels except for the input channel can be used. Each channel can
		be used only once. \n
			:param output_source: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param output: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Output')
		"""
		param = Conversions.enum_scalar_to_str(output_source, enums.Source)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		output_cmd_val = self._cmd_group.get_repcap_cmd_value(output, repcap.Output)
		self._core.io.write(f'POWer{power_cmd_val}:ONOFf:OUTPut{output_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default, output=repcap.Output.Default) -> enums.Source:
		"""POWer<*>:ONOFf:OUTPut<*>[:SOURce] \n
		Snippet: value: enums.Source = driver.power.onOff.output.source.get(power = repcap.Power.Default, output = repcap.Output.Default) \n
		Selects the channel of the output signal. All analog channels except for the input channel can be used. Each channel can
		be used only once. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param output: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Output')
			:return: output_source: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		output_cmd_val = self._cmd_group.get_repcap_cmd_value(output, repcap.Output)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:OUTPut{output_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
