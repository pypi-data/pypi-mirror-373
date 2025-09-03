from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RwbItCls:
	"""RwbIt commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rwbIt", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusIxcReadWriteBit:
		"""SBUS<*>:I3C:FRAMe<*>:RWBit \n
		Snippet: value: enums.SbusIxcReadWriteBit = driver.sbus.i3C.frame.rwbIt.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the value of the R/W bit of the selected frame. The value '0' denotes 'Write', the value '1' denotes 'Read'. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: rwb_it_value: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I3C:FRAMe{frame_cmd_val}:RWBit?')
		return Conversions.str_to_scalar_enum(response, enums.SbusIxcReadWriteBit)
