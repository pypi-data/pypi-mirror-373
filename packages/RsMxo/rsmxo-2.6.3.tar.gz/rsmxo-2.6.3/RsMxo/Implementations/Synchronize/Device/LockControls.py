from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LockControlsCls:
	"""LockControls commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lockControls", core, parent)

	def set(self, rem_dev_lock_controls: bool, device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:LOCKcontrols \n
		Snippet: driver.synchronize.device.lockControls.set(rem_dev_lock_controls = False, device = repcap.Device.Default) \n
		No command help available \n
			:param rem_dev_lock_controls: No help available
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		param = Conversions.bool_to_str(rem_dev_lock_controls)
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:LOCKcontrols {param}')

	def get(self, device=repcap.Device.Default) -> bool:
		"""SYNChronize:DEVice<*>:LOCKcontrols \n
		Snippet: value: bool = driver.synchronize.device.lockControls.get(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:return: rem_dev_lock_controls: No help available"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		response = self._core.io.query_str(f'SYNChronize:DEVice{device_cmd_val}:LOCKcontrols?')
		return Conversions.str_to_bool(response)
