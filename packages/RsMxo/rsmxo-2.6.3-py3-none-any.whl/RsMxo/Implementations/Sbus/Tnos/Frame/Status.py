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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusTnosFrameState:
		"""SBUS<*>:TNOS:FRAMe<*>:STATus \n
		Snippet: value: enums.SbusTnosFrameState = driver.sbus.tnos.frame.status.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the state of the frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_state:
				- OK: The frame has no error, it is valid.
				- EPRMble: Preamble error, the hex value of the preamble field is different from 0x55555555555555 (56 alternating 0's and 1's) .
				- ESFD: SFD error, the hex value of the SFD field is different from 0xD5
				- EESD: ESD error, the value of the ESD field does not correspond to the symbol pair 'ESD, ESDOK'
				- ECRC: CRC error, the value of the FCS field does not match the calculated CRC.
				- ELEN: Length error, the number of bits in the specified frame is higher or lower than expected.
				- INComplete: The frame is incomplete"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:TNOS:FRAMe{frame_cmd_val}:STATus?')
		return Conversions.str_to_scalar_enum(response, enums.SbusTnosFrameState)
