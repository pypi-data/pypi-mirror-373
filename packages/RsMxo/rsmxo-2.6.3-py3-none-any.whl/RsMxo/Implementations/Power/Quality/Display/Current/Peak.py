from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PeakCls:
	"""Peak commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("peak", core, parent)

	def set(self, shw_curr_peak: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:DISPlay:CURRent:PEAK \n
		Snippet: driver.power.quality.display.current.peak.set(shw_curr_peak = False, power = repcap.Power.Default) \n
		Enables the current peak measurement for the power quality analysis. \n
			:param shw_curr_peak: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(shw_curr_peak)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:DISPlay:CURRent:PEAK {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>:QUALity:DISPlay:CURRent:PEAK \n
		Snippet: value: bool = driver.power.quality.display.current.peak.get(power = repcap.Power.Default) \n
		Enables the current peak measurement for the power quality analysis. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: shw_curr_peak: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:DISPlay:CURRent:PEAK?')
		return Conversions.str_to_bool(response)
