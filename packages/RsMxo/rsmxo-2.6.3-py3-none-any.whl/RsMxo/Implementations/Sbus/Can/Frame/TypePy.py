from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusCanFrameType:
		"""SBUS<*>:CAN:FRAMe<*>:TYPE \n
		Snippet: value: enums.SbusCanFrameType = driver.sbus.can.frame.typePy.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the frame type of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_type: CBFF: classical base frame format data CBFRemote: classical base frame format remote CEFF: classical extended frame format data CEFRemote: classical extended frame format remote FBFF: FD base frame format FEFF: FD extended frame format XLFF: XL frame format ERR: error OVLD: overload"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FRAMe{frame_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanFrameType)
