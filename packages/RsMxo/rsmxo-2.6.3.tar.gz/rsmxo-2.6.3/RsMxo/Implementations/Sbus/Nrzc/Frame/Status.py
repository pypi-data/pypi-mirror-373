from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StatusCls:
	"""Status commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("status", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusNrzcFrameState:
		"""SBUS<*>:NRZC:FRAMe<*>:STATus \n
		Snippet: value: enums.SbusNrzcFrameState = driver.sbus.nrzc.frame.status.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the overall state of the specified frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_state:
				- OK: The frame is valid.
				- LENGth: Length of the frame is not as expected, indicating an error.
				- CRC: The checksum of the frame is not as expected, indicating an error.
				- PARity: Parity is not as expected, indicating an error.
				- INComplete: The frame is incomplete."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:FRAMe{frame_cmd_val}:STATus?')
		return Conversions.str_to_scalar_enum(response, enums.SbusNrzcFrameState)
