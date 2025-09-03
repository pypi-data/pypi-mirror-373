from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OnumberCls:
	"""Onumber commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("onumber", core, parent)

	def set(self, output_count: int, power=repcap.Power.Default) -> None:
		"""POWer<*>:ONOFf:ONUMber \n
		Snippet: driver.power.onOff.onumber.set(output_count = 1, power = repcap.Power.Default) \n
		Sets the number of outputs to be used in the measurement. \n
			:param output_count: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(output_count)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:ONOFf:ONUMber {param}')

	def get(self, power=repcap.Power.Default) -> int:
		"""POWer<*>:ONOFf:ONUMber \n
		Snippet: value: int = driver.power.onOff.onumber.get(power = repcap.Power.Default) \n
		Sets the number of outputs to be used in the measurement. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: output_count: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:ONUMber?')
		return Conversions.str_to_int(response)
