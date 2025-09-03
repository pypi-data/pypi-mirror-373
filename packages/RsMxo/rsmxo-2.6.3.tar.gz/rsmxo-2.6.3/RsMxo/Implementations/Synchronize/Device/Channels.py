from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ChannelsCls:
	"""Channels commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("channels", core, parent)

	def set(self, sources: List[enums.AnalogChannels], device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:CHANnels \n
		Snippet: driver.synchronize.device.channels.set(sources = [AnalogChannels.C1, AnalogChannels.C8], device = repcap.Device.Default) \n
		No command help available \n
			:param sources: No help available
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		param = Conversions.enum_list_to_str(sources, enums.AnalogChannels)
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:CHANnels {param}')

	# noinspection PyTypeChecker
	def get(self, device=repcap.Device.Default) -> List[enums.AnalogChannels]:
		"""SYNChronize:DEVice<*>:CHANnels \n
		Snippet: value: List[enums.AnalogChannels] = driver.synchronize.device.channels.get(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:return: sources: No help available"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		response = self._core.io.query_str(f'SYNChronize:DEVice{device_cmd_val}:CHANnels?')
		return Conversions.str_to_list_enum(response, enums.AnalogChannels)
