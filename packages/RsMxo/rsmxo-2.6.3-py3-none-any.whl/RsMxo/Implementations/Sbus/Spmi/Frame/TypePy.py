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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> enums.SbusSpmiFrameType:
		"""SBUS<*>:SPMI:FRAMe<*>:TYPE \n
		Snippet: value: enums.SbusSpmiFrameType = driver.sbus.spmi.frame.typePy.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the frame type. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_type: RZWR: register 0 write RWR: register write RRD: register read ERWR: extended register write ERRD: extended register read ERWL: extended register write long ERRL: extended register read long MAWR: main write MARD: main read BMRD: device descriptor block main read BSRD: device descriptor block sub read TBOW: transfer bus ownership REST: reset SLEP: sleep SHUT: shutdown WAK: wakeup AUTH: authenticate INV: invalid UNKN: unknown ARB: arbitration frame"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPMI:FRAMe{frame_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSpmiFrameType)
