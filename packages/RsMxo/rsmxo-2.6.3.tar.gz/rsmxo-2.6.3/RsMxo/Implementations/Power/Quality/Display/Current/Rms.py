from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RmsCls:
	"""Rms commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rms", core, parent)

	def set(self, show_current_rms: bool, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:DISPlay:CURRent:RMS \n
		Snippet: driver.power.quality.display.current.rms.set(show_current_rms = False, power = repcap.Power.Default) \n
		Enables the current RMS measurement for the power quality analysis. \n
			:param show_current_rms: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(show_current_rms)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:DISPlay:CURRent:RMS {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""POWer<*>:QUALity:DISPlay:CURRent:RMS \n
		Snippet: value: bool = driver.power.quality.display.current.rms.get(power = repcap.Power.Default) \n
		Enables the current RMS measurement for the power quality analysis. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: show_current_rms: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:DISPlay:CURRent:RMS?')
		return Conversions.str_to_bool(response)
