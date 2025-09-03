from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BitOrderCls:
	"""BitOrder commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bitOrder", core, parent)

	def set(self, bit_order: enums.BitOrder, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:FLD<*>:BITorder \n
		Snippet: driver.sbus.nrzu.formatPy.frame.fld.bitOrder.set(bit_order = enums.BitOrder.LSBF, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies, in which order the algorithm evaluates the bits of the condition value of the selected field in the selected
		frame. \n
			:param bit_order:
				- LSBF: Least significant bit first
				- MSBF: Most significant bit first
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')"""
		param = Conversions.enum_scalar_to_str(bit_order, enums.BitOrder)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:BITorder {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.BitOrder:
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:FLD<*>:BITorder \n
		Snippet: value: enums.BitOrder = driver.sbus.nrzu.formatPy.frame.fld.bitOrder.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies, in which order the algorithm evaluates the bits of the condition value of the selected field in the selected
		frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: bit_order:
				- LSBF: Least significant bit first
				- MSBF: Most significant bit first"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:BITorder?')
		return Conversions.str_to_scalar_enum(response, enums.BitOrder)
