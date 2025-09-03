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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusSentFrameType:
		"""SBUS<*>:SENT:FRAMe<*>:TYPE \n
		Snippet: value: enums.SbusSentFrameType = driver.sbus.sent.frame.typePy.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the type of SENT message. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_type: TRSQ: transmission sequence SMSG: short serial message ESSM: enhanced 12 bit message ELSM: enhanced 16 bit message"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:FRAMe{frame_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSentFrameType)
