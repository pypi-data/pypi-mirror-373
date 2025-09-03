from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IdTypeCls:
	"""IdType commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("idType", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusCanIdentifierType:
		"""SBUS<*>:CAN:FRAMe<*>:IDTYpe \n
		Snippet: value: enums.SbusCanIdentifierType = driver.sbus.can.frame.idType.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the identifier type of the selected frame, the identifier format of data and remote frames. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: identifier_type: B11: standard format, 11 bit B29: extended format, 29 bit"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FRAMe{frame_cmd_val}:IDTYpe?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanIdentifierType)
