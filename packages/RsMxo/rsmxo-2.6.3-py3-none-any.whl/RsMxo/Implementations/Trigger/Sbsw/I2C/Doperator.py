from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DoperatorCls:
	"""Doperator commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("doperator", core, parent)

	def set(self, frame: str, field: str, operator: enums.OperatorB) -> None:
		"""TRIGger:SBSW:I2C:DOPerator \n
		Snippet: driver.trigger.sbsw.i2C.doperator.set(frame = 'abc', field = 'abc', operator = enums.OperatorB.EQUal) \n
		Sets the operator for the data pattern of the software trigger in the selected field of the selected frame. \n
			:param frame: No help available
			:param field: No help available
			:param operator: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('operator', operator, DataType.Enum, enums.OperatorB))
		self._core.io.write(f'TRIGger:SBSW:I2C:DOPerator {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self) -> enums.OperatorB:
		"""TRIGger:SBSW:I2C:DOPerator \n
		Snippet: value: enums.OperatorB = driver.trigger.sbsw.i2C.doperator.get() \n
		Sets the operator for the data pattern of the software trigger in the selected field of the selected frame. \n
			:return: operator: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:I2C:DOPerator?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)
