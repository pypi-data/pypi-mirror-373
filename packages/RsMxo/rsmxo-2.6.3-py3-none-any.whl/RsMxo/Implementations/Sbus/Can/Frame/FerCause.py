from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FerCauseCls:
	"""FerCause commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ferCause", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.FormErrorCause:
		"""SBUS<*>:CAN:FRAMe<*>:FERCause \n
		Snippet: value: enums.FormErrorCause = driver.sbus.can.frame.ferCause.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns information on a form error, if the frame status query (method RsMxo.Sbus.Can.Frame.Status.get_) returned a form
		error. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: form_error_cause: CRCDerror = CRC delimiter error ACKDerror = ACK delimiter error FSBE = fixed stuff bit error (CAN FD ISO only) RESerror = reserved bit error"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FRAMe{frame_cmd_val}:FERCause?')
		return Conversions.str_to_scalar_enum(response, enums.FormErrorCause)
