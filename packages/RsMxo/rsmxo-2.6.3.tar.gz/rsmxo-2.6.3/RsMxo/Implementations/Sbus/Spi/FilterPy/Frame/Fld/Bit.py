from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BitCls:
	"""Bit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bit", core, parent)

	def set(self, bit_state: enums.SbusBitState, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""SBUS<*>:SPI:FILTer:FRAMe<*>:FLD<*>:BIT \n
		Snippet: driver.sbus.spi.filterPy.frame.fld.bit.set(bit_state = enums.SbusBitState.DC, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the data pattern in the selected field of the selected frame. \n
			:param bit_state: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.enum_scalar_to_str(bit_state, enums.SbusBitState)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPI:FILTer:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:BIT {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.SbusBitState:
		"""SBUS<*>:SPI:FILTer:FRAMe<*>:FLD<*>:BIT \n
		Snippet: value: enums.SbusBitState = driver.sbus.spi.filterPy.frame.fld.bit.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the data pattern in the selected field of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: bit_state: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPI:FILTer:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:BIT?')
		return Conversions.str_to_scalar_enum(response, enums.SbusBitState)
