from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IoperatorCls:
	"""Ioperator commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ioperator", core, parent)

	def set(self, frame: str, field: str, operator: enums.OperatorA, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:FILTer:IOPerator \n
		Snippet: driver.sbus.sent.filterPy.ioperator.set(frame = 'abc', field = 'abc', operator = enums.OperatorA.ANY, serialBus = repcap.SerialBus.Default) \n
		Sets the operator for the index in the selected field of the selected frame. \n
			:param frame: No help available
			:param field: No help available
			:param operator: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('operator', operator, DataType.Enum, enums.OperatorA))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:FILTer:IOPerator {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.OperatorA:
		"""SBUS<*>:SENT:FILTer:IOPerator \n
		Snippet: value: enums.OperatorA = driver.sbus.sent.filterPy.ioperator.get(serialBus = repcap.SerialBus.Default) \n
		Sets the operator for the index in the selected field of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: operator: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:FILTer:IOPerator?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorA)
