from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BitCls:
	"""Bit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bit", core, parent)

	def set(self, frame: str, field: str, bit: enums.SbusBitState) -> None:
		"""TRIGger:SBSW:CAN:BIT \n
		Snippet: driver.trigger.sbsw.can.bit.set(frame = 'abc', field = 'abc', bit = enums.SbusBitState.DC) \n
		Sets the bit state of a field that only consists of one bit for the software trigger. \n
			:param frame: No help available
			:param field: No help available
			:param bit: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('bit', bit, DataType.Enum, enums.SbusBitState))
		self._core.io.write(f'TRIGger:SBSW:CAN:BIT {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self) -> enums.SbusBitState:
		"""TRIGger:SBSW:CAN:BIT \n
		Snippet: value: enums.SbusBitState = driver.trigger.sbsw.can.bit.get() \n
		Sets the bit state of a field that only consists of one bit for the software trigger. \n
			:return: bit: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:CAN:BIT?')
		return Conversions.str_to_scalar_enum(response, enums.SbusBitState)
