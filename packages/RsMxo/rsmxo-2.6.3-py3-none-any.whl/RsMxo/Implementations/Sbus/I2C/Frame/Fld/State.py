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
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.SbusI2cFrameState:
		"""SBUS<*>:I2C:FRAMe<*>:FLD<*>:STATe \n
		Snippet: value: enums.SbusI2cFrameState = driver.sbus.i2C.frame.fld.state.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Returns the overall state of the specified field in the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: state:
				- OK: The field has no error, it is valid.
				- ADDifferent: 10-bit read address different. For a read access on a 10-bit address, the first address byte is sent twice, first as write, the second as read. The first 7 bits of the byte must be identical. If they are not identical, the ADDiffernt error is indicated.
				- NOSTop: The stop bit is missing.
				- UNKNown: Unknown field type detected.
				- INComplete: The field is not completely contained in the acquisition. The acquired part of the field is usually valid, but cannot always be trusted."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I2C:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.SbusI2cFrameState)
