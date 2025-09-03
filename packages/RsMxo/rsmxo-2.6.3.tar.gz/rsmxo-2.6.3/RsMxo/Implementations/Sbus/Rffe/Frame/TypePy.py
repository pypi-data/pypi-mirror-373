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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusRffeSeqType:
		"""SBUS<*>:RFFE:FRAMe<*>:TYPE \n
		Snippet: value: enums.SbusRffeSeqType = driver.sbus.rffe.frame.typePy.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the type of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: type_py:
				- RZWR: Register 0 write
				- RWR: Register write
				- RRD: Register read
				- ERWR: Extended register write
				- ERRD: Extended register read
				- ERWL: Extended register write long
				- ERRL: Extended register read long
				- MRD: Main device read
				- MWR: Main device write
				- MOHO: Main device Ownership Handove
				- IRSUM: Interrupt summary and notification
				- MSKW: Masked write
				- MCTR: Main device context transfer read
				- MCTW: Main device context transfer write
				- UNDEF: Undefined frame type
				- UNKN: Unknown frame type
				- ERRor: The bits defining the command sequence are not valid, no supported command sequence"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RFFE:FRAMe{frame_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusRffeSeqType)
