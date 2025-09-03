from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ColorCls:
	"""Color commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("color", core, parent)

	def set(self, color: int, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> None:
		"""SBUS<*>:NRZC:FORMat:FRAMe<*>:COLor \n
		Snippet: driver.sbus.nrzc.formatPy.frame.color.set(color = 1, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Specifies the color for the frame description of the selected frame. \n
			:param color: Use 32-bit RGB encoding in decimal format.
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
		"""
		param = Conversions.decimal_value_to_str(color)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:FRAMe{frame_cmd_val}:COLor {param}')

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> int:
		"""SBUS<*>:NRZC:FORMat:FRAMe<*>:COLor \n
		Snippet: value: int = driver.sbus.nrzc.formatPy.frame.color.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Specifies the color for the frame description of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: color: Use 32-bit RGB encoding in decimal format."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:FRAMe{frame_cmd_val}:COLor?')
		return Conversions.str_to_int(response)
