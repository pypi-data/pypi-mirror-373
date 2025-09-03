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

	def set(self, enable: bool, frame=repcap.Frame.Default) -> None:
		"""TRIGger:SBSW:CAN:FRAMe<*>:ENABle \n
		Snippet: driver.trigger.sbsw.can.frame.enable.set(enable = False, frame = repcap.Frame.Default) \n
		Enables or disables the checking condition for the selected frame for the software trigger. \n
			:param enable: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
		"""
		param = Conversions.bool_to_str(enable)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		self._core.io.write(f'TRIGger:SBSW:CAN:FRAMe{frame_cmd_val}:ENABle {param}')

	def get(self, frame=repcap.Frame.Default) -> bool:
		"""TRIGger:SBSW:CAN:FRAMe<*>:ENABle \n
		Snippet: value: bool = driver.trigger.sbsw.can.frame.enable.get(frame = repcap.Frame.Default) \n
		Enables or disables the checking condition for the selected frame for the software trigger. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: enable: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'TRIGger:SBSW:CAN:FRAMe{frame_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
