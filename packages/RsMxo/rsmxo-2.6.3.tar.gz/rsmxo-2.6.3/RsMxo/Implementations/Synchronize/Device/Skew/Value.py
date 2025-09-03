from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, skew: float, device=repcap.Device.Default) -> None:
		"""SYNChronize:DEVice<*>:SKEW[:VALue] \n
		Snippet: driver.synchronize.device.skew.value.set(skew = 1.0, device = repcap.Device.Default) \n
		No command help available \n
			:param skew: No help available
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
		"""
		param = Conversions.decimal_value_to_str(skew)
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		self._core.io.write(f'SYNChronize:DEVice{device_cmd_val}:SKEW:VALue {param}')

	def get(self, device=repcap.Device.Default) -> float:
		"""SYNChronize:DEVice<*>:SKEW[:VALue] \n
		Snippet: value: float = driver.synchronize.device.skew.value.get(device = repcap.Device.Default) \n
		No command help available \n
			:param device: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Device')
			:return: skew: No help available"""
		device_cmd_val = self._cmd_group.get_repcap_cmd_value(device, repcap.Device)
		response = self._core.io.query_str(f'SYNChronize:DEVice{device_cmd_val}:SKEW:VALue?')
		return Conversions.str_to_float(response)
