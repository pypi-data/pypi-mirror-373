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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusQspiFrameState:
		"""SBUS<*>:QSPI:FRAMe<*>:STATus \n
		Snippet: value: enums.SbusQspiFrameState = driver.sbus.qspi.frame.status.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the overall state of the specified frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_state: OK: the frame is valid. OPCode: operation code. INComplete: INComplete word. The word does not have the expected word length. LENGth: The frame is not contained in the acquisition."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:FRAMe{frame_cmd_val}:STATus?')
		return Conversions.str_to_scalar_enum(response, enums.SbusQspiFrameState)
