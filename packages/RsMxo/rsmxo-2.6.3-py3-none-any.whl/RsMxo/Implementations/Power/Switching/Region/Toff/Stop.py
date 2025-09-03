from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StopCls:
	"""Stop commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stop", core, parent)

	def set(self, t_4_position: float, power=repcap.Power.Default) -> None:
		"""POWer<*>:SWITching:REGion:TOFF:STOP \n
		Snippet: driver.power.switching.region.toff.stop.set(t_4_position = 1.0, power = repcap.Power.Default) \n
		Sets the start time for the non-conduction area in relation to the trigger point. This value is also the end time of the
		turn off area. \n
			:param t_4_position: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(t_4_position)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:SWITching:REGion:TOFF:STOP {param}')

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:SWITching:REGion:TOFF:STOP \n
		Snippet: value: float = driver.power.switching.region.toff.stop.get(power = repcap.Power.Default) \n
		Sets the start time for the non-conduction area in relation to the trigger point. This value is also the end time of the
		turn off area. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: t_4_position: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:REGion:TOFF:STOP?')
		return Conversions.str_to_float(response)
