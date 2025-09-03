from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ConnectCls:
	"""Connect commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("connect", core, parent)

	def set(self, state: bool, device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:CONNect \n
		Snippet: driver.synchronize.device.connect.set(state = False, device = repcap.Device.Default) \n
		No command help available \n
			:param state: No help available
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		param = Conversions.bool_to_str(state)
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:CONNect {param}')

	def get(self, device=repcap.Device.Default) -> bool:
		"""SYNChronize:DEVice<*>:CONNect \n
		Snippet: value: bool = driver.synchronize.device.connect.get(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:return: state: No help available"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		response = self._core.io.query_str(f'SYNChronize:DEVice{device_cmd_val}:CONNect?')
		return Conversions.str_to_bool(response)
