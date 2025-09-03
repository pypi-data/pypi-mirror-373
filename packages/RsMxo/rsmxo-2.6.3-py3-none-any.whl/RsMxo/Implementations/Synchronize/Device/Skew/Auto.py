from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AutoCls:
	"""Auto commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("auto", core, parent)

	def set(self, device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:SKEW:AUTO \n
		Snippet: driver.synchronize.device.skew.auto.set(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:SKEW:AUTO')

	def set_and_wait(self, device=repcap.Device.Default, opc_timeout_ms: int = -1) -> None:
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		"""SYNChronize:DEVice<*>:SKEW:AUTO \n
		Snippet: driver.synchronize.device.skew.auto.set_and_wait(device = repcap.Device.Default) \n
		No command help available \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SYNChronize:DEVice{device_cmd_val}:SKEW:AUTO', opc_timeout_ms)
