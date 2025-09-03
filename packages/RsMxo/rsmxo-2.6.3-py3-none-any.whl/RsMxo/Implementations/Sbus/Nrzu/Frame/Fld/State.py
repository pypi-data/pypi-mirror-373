from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.SbusNrzcFrameState:
		"""SBUS<*>:NRZU:FRAMe<*>:FLD<*>:STATe \n
		Snippet: value: enums.SbusNrzcFrameState = driver.sbus.nrzu.frame.fld.state.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Returns the overall state of the specified field in the specified frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: state:
				- OK: The field has no error, it is valid.
				- LENGth: The length of the field is not as expected, indicating an error.
				- CRC: The CRC of the frame is not as expected, indicating an error.
				- PARity: Parity is not as expected, indicating an error
				- INComplete: The frame is incomplete."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZU:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.SbusNrzcFrameState)
