from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DoperatorCls:
	"""Doperator commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("doperator", core, parent)

	def set(self, data_operator: enums.OperatorB, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""TRIGger:SBSW:SWIRe:FRAMe<*>:FLD<*>:DOPerator \n
		Snippet: driver.trigger.sbsw.swire.frame.fld.doperator.set(data_operator = enums.OperatorB.EQUal, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the data pattern of the software trigger in the selected field of the selected frame. \n
			:param data_operator: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.enum_scalar_to_str(data_operator, enums.OperatorB)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'TRIGger:SBSW:SWIRe:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:DOPerator {param}')

	# noinspection PyTypeChecker
	def get(self, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.OperatorB:
		"""TRIGger:SBSW:SWIRe:FRAMe<*>:FLD<*>:DOPerator \n
		Snippet: value: enums.OperatorB = driver.trigger.sbsw.swire.frame.fld.doperator.get(frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the data pattern of the software trigger in the selected field of the selected frame. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: data_operator: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'TRIGger:SBSW:SWIRe:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:DOPerator?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)
