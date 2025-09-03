from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, enable: bool, power=repcap.Power.Default, output=repcap.Output.Default) -> None:
		"""POWer<*>:ONOFf:OUTPut<*>:DISPlay:RESult[:ENABle] \n
		Snippet: driver.power.onOff.output.display.result.enable.set(enable = False, power = repcap.Power.Default, output = repcap.Output.Default) \n
		Activates the indicated output line. \n
			:param enable: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param output: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Output')
		"""
		param = Conversions.bool_to_str(enable)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		output_cmd_val = self._cmd_group.get_repcap_cmd_value(output, repcap.Output)
		self._core.io.write(f'POWer{power_cmd_val}:ONOFf:OUTPut{output_cmd_val}:DISPlay:RESult:ENABle {param}')

	def get(self, power=repcap.Power.Default, output=repcap.Output.Default) -> bool:
		"""POWer<*>:ONOFf:OUTPut<*>:DISPlay:RESult[:ENABle] \n
		Snippet: value: bool = driver.power.onOff.output.display.result.enable.get(power = repcap.Power.Default, output = repcap.Output.Default) \n
		Activates the indicated output line. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param output: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Output')
			:return: enable: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		output_cmd_val = self._cmd_group.get_repcap_cmd_value(output, repcap.Output)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:OUTPut{output_cmd_val}:DISPlay:RESult:ENABle?')
		return Conversions.str_to_bool(response)
