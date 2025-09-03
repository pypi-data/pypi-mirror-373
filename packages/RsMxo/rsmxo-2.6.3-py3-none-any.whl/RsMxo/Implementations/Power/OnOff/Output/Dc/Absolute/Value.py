from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, dc_threshold_abs: float, power=repcap.Power.Default, output=repcap.Output.Default) -> None:
		"""POWer<*>:ONOFf:OUTPut<*>:DC:ABSolute[:VALue] \n
		Snippet: driver.power.onOff.output.dc.absolute.value.set(dc_threshold_abs = 1.0, power = repcap.Power.Default, output = repcap.Output.Default) \n
		Sets the threshold for the selected output signal. \n
			:param dc_threshold_abs: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param output: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Output')
		"""
		param = Conversions.decimal_value_to_str(dc_threshold_abs)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		output_cmd_val = self._cmd_group.get_repcap_cmd_value(output, repcap.Output)
		self._core.io.write(f'POWer{power_cmd_val}:ONOFf:OUTPut{output_cmd_val}:DC:ABSolute:VALue {param}')

	def get(self, power=repcap.Power.Default, output=repcap.Output.Default) -> float:
		"""POWer<*>:ONOFf:OUTPut<*>:DC:ABSolute[:VALue] \n
		Snippet: value: float = driver.power.onOff.output.dc.absolute.value.get(power = repcap.Power.Default, output = repcap.Output.Default) \n
		Sets the threshold for the selected output signal. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param output: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Output')
			:return: dc_threshold_abs: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		output_cmd_val = self._cmd_group.get_repcap_cmd_value(output, repcap.Output)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:OUTPut{output_cmd_val}:DC:ABSolute:VALue?')
		return Conversions.str_to_float(response)
