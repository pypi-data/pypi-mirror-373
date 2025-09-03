from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DisplayCls:
	"""Display commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("display", core, parent)

	def set(self, rem_dev_disp_upd: bool, device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:DISPlay \n
		Snippet: driver.synchronize.device.display.set(rem_dev_disp_upd = False, device = repcap.Device.Default) \n
		No command help available \n
			:param rem_dev_disp_upd: No help available
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		param = Conversions.bool_to_str(rem_dev_disp_upd)
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:DISPlay {param}')

	def get(self, device=repcap.Device.Default) -> bool:
		"""SYNChronize:DEVice<*>:DISPlay \n
		Snippet: value: bool = driver.synchronize.device.display.get(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:return: rem_dev_disp_upd: No help available"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		response = self._core.io.query_str(f'SYNChronize:DEVice{device_cmd_val}:DISPlay?')
		return Conversions.str_to_bool(response)
