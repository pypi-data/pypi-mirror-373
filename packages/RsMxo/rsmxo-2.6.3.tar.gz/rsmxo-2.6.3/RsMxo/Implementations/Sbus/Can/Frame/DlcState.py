from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DlcStateCls:
	"""DlcState commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dlcState", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusCanFrameOverallState:
		"""SBUS<*>:CAN:FRAMe<*>:DLCState \n
		Snippet: value: enums.SbusCanFrameOverallState = driver.sbus.can.frame.dlcState.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Return the states of the state of data length code. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_dlc_state: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FRAMe{frame_cmd_val}:DLCState?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanFrameOverallState)
