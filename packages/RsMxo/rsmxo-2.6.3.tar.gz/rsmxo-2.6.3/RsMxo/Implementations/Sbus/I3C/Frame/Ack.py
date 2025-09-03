from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AckCls:
	"""Ack commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ack", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusAckBit:
		"""SBUS<*>:I3C:FRAMe<*>:ACK \n
		Snippet: value: enums.SbusAckBit = driver.sbus.i3C.frame.ack.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the value of the acknowledge bit for the selected frame. Because this ACK bit is transmitted right after the
		address field, it acknowledges receiving the address. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: ack_bit_value: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I3C:FRAMe{frame_cmd_val}:ACK?')
		return Conversions.str_to_scalar_enum(response, enums.SbusAckBit)
