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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusHbtoFrameState:
		"""SBUS<*>:HBTO:FRAMe<*>:STATus \n
		Snippet: value: enums.SbusHbtoFrameState = driver.sbus.hbto.frame.status.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the overall state of the frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_state:
				- OK: Valid frame.
				- EPRMble: Erroneous frame due to preamble error.
				- ESFD: Erroneous frame due to SFD error.
				- ELENgth: Erroneous frame due to length / type error.
				- ECRC: Erroneous frame due to CRC error.
				- UNCorrelated: Uncorrelated frame
				- INComplete: Frame is inclompete"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:HBTO:FRAMe{frame_cmd_val}:STATus?')
		return Conversions.str_to_scalar_enum(response, enums.SbusHbtoFrameState)
