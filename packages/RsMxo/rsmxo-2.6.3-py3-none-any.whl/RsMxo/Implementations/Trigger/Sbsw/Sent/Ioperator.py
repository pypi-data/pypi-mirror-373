from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IoperatorCls:
	"""Ioperator commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ioperator", core, parent)

	def set(self, frame: str, field: str, operator: enums.OperatorA) -> None:
		"""TRIGger:SBSW:SENT:IOPerator \n
		Snippet: driver.trigger.sbsw.sent.ioperator.set(frame = 'abc', field = 'abc', operator = enums.OperatorA.ANY) \n
		Sets the operator for the index in the selected field of the selected frame for the software trigger. \n
			:param frame: No help available
			:param field: No help available
			:param operator: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('operator', operator, DataType.Enum, enums.OperatorA))
		self._core.io.write(f'TRIGger:SBSW:SENT:IOPerator {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self) -> enums.OperatorA:
		"""TRIGger:SBSW:SENT:IOPerator \n
		Snippet: value: enums.OperatorA = driver.trigger.sbsw.sent.ioperator.get() \n
		Sets the operator for the index in the selected field of the selected frame for the software trigger. \n
			:return: operator: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:SENT:IOPerator?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorA)
