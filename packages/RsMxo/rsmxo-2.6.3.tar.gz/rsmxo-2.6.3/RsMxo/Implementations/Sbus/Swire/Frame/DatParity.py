from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DatParityCls:
	"""DatParity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("datParity", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusSwireFrameState:
		"""SBUS<*>:SWIRe:FRAMe<*>:DATParity \n
		Snippet: value: enums.SbusSwireFrameState = driver.sbus.swire.frame.datParity.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		If the frame has the Data field, the command returns the parity state of this field, which can take values of OK or
		PARity. The Data field only appears in Data and Time frames, see Figure 'SpaceWire data characters' and Figure 'SpaceWire
		control codes'. If the frame has no Data field, the command can return the states LENGth, AMBiguous or INComplete of the
		frame, as described below. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: parity_data:
				- OK: The parity check for the Data field passes.
				- PARity: The parity of the Data field is not correct.
				- LENGth: Regardless of the Data field, the length of the frame is not as expected, indicating an error
				- AMBiguous: Regardless of the Data field, the frame is ambiguous.
				- INComplete: Regardless of the Data field, the frame is incomplete."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SWIRe:FRAMe{frame_cmd_val}:DATParity?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSwireFrameState)
