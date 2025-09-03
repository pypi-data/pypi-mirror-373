from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimeBaseSyncCls:
	"""TimeBaseSync commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("timeBaseSync", core, parent)

	def set(self, sync_timebase: bool, device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:TIMebasesync \n
		Snippet: driver.synchronize.device.timeBaseSync.set(sync_timebase = False, device = repcap.Device.Default) \n
		No command help available \n
			:param sync_timebase: No help available
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		param = Conversions.bool_to_str(sync_timebase)
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:TIMebasesync {param}')

	def get(self, device=repcap.Device.Default) -> bool:
		"""SYNChronize:DEVice<*>:TIMebasesync \n
		Snippet: value: bool = driver.synchronize.device.timeBaseSync.get(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:return: sync_timebase: No help available"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		response = self._core.io.query_str(f'SYNChronize:DEVice{device_cmd_val}:TIMebasesync?')
		return Conversions.str_to_bool(response)
