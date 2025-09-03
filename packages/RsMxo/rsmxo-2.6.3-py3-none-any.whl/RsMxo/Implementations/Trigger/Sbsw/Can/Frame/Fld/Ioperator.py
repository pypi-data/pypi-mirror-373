from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IoperatorCls:
	"""Ioperator commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ioperator", core, parent)

	def set(self, index_operator: enums.OperatorA, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""TRIGger:SBSW:CAN:FRAMe<*>:FLD<*>:IOPerator \n
		Snippet: driver.trigger.sbsw.can.frame.fld.ioperator.set(index_operator = enums.OperatorA.ANY, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the index in the selected field of the selected frame for the software trigger. \n
			:param index_operator: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.enum_scalar_to_str(index_operator, enums.OperatorA)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'TRIGger:SBSW:CAN:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IOPerator {param}')

	# noinspection PyTypeChecker
	def get(self, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.OperatorA:
		"""TRIGger:SBSW:CAN:FRAMe<*>:FLD<*>:IOPerator \n
		Snippet: value: enums.OperatorA = driver.trigger.sbsw.can.frame.fld.ioperator.get(frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the index in the selected field of the selected frame for the software trigger. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: index_operator: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'TRIGger:SBSW:CAN:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IOPerator?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorA)
