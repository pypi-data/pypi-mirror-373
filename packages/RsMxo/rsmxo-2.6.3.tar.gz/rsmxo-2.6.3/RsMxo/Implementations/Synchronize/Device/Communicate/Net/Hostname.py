from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.Utilities import trim_str_response
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HostnameCls:
	"""Hostname commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hostname", core, parent)

	def set(self, hostname: str, device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:COMMunicate:NET[:HOSTname] \n
		Snippet: driver.synchronize.device.communicate.net.hostname.set(hostname = 'abc', device = repcap.Device.Default) \n
		No command help available \n
			:param hostname: No help available
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		param = Conversions.value_to_quoted_str(hostname)
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:COMMunicate:NET:HOSTname {param}')

	def get(self, device=repcap.Device.Default) -> str:
		"""SYNChronize:DEVice<*>:COMMunicate:NET[:HOSTname] \n
		Snippet: value: str = driver.synchronize.device.communicate.net.hostname.get(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:return: hostname: No help available"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		response = self._core.io.query_str(f'SYNChronize:DEVice{device_cmd_val}:COMMunicate:NET:HOSTname?')
		return trim_str_response(response)
