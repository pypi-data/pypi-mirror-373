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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusHbtoFrameType:
		"""SBUS<*>:HBTO:FRAMe<*>:TYPE \n
		Snippet: value: enums.SbusHbtoFrameType = driver.sbus.hbto.frame.typePy.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the type of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_type:
				- IDLE: IDLE frame. This frame is used for clock synchronization.
				- MAC: MAC frame. This frame contains information that define how to go about transmitting and receiving frames.
				- FILLer: Filler frame. The frame is used to maintain transmission activity.
				- UNKNown: No meaningful frame can be determined."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:HBTO:FRAMe{frame_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusHbtoFrameType)
