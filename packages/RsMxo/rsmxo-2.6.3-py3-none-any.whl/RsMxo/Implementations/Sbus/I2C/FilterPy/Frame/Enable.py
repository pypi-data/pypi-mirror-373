from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, enable: bool, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> None:
		"""SBUS<*>:I2C:FILTer:FRAMe<*>:ENABle \n
		Snippet: driver.sbus.i2C.filterPy.frame.enable.set(enable = False, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Enables or disables the specific frame to be filtered on. \n
			:param enable: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
		"""
		param = Conversions.bool_to_str(enable)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:I2C:FILTer:FRAMe{frame_cmd_val}:ENABle {param}')

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> bool:
		"""SBUS<*>:I2C:FILTer:FRAMe<*>:ENABle \n
		Snippet: value: bool = driver.sbus.i2C.filterPy.frame.enable.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Enables or disables the specific frame to be filtered on. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: enable: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I2C:FILTer:FRAMe{frame_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
