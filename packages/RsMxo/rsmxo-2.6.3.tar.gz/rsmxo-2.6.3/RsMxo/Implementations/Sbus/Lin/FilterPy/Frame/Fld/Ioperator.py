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

	def set(self, index_operator: enums.OperatorA, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""SBUS<*>:LIN:FILTer:FRAMe<*>:FLD<*>:IOPerator \n
		Snippet: driver.sbus.lin.filterPy.frame.fld.ioperator.set(index_operator = enums.OperatorA.ANY, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the index in the selected field of the selected frame. \n
			:param index_operator: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.enum_scalar_to_str(index_operator, enums.OperatorA)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:LIN:FILTer:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IOPerator {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> enums.OperatorA:
		"""SBUS<*>:LIN:FILTer:FRAMe<*>:FLD<*>:IOPerator \n
		Snippet: value: enums.OperatorA = driver.sbus.lin.filterPy.frame.fld.ioperator.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the operator for the index in the selected field of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: index_operator: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:LIN:FILTer:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IOPerator?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorA)
