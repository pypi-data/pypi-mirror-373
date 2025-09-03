from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AaccessCls:
	"""Aaccess commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("aaccess", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusAckBit:
		"""SBUS<*>:I2C:FRAMe<*>:AACCess \n
		Snippet: value: enums.SbusAckBit = driver.sbus.i2C.frame.aaccess.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the address acknowledge bit value for the indicated frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: address_ack_bit: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I2C:FRAMe{frame_cmd_val}:AACCess?')
		return Conversions.str_to_scalar_enum(response, enums.SbusAckBit)
