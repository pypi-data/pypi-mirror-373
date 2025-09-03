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

	def set(self, first: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>:SWITching:DISPlay:POWer:WAVeform[:ENABle] \n
		Snippet: driver.power.switching.display.power.waveform.enable.set(first = False, power = repcap.Power.Default) \n
		No command help available \n
			:param first: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(first)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:SWITching:DISPlay:POWer:WAVeform:ENABle {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>:SWITching:DISPlay:POWer:WAVeform[:ENABle] \n
		Snippet: value: bool = driver.power.switching.display.power.waveform.enable.get(power = repcap.Power.Default) \n
		No command help available \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: first: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:DISPlay:POWer:WAVeform:ENABle?')
		return Conversions.str_to_bool(response)
