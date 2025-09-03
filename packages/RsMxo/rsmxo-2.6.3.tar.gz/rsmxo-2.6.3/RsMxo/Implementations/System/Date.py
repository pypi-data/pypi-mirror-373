from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Types import DataType
from ...Internal.StructBase import StructBase
from ...Internal.ArgStruct import ArgStruct
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DateCls:
	"""Date commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("date", core, parent)

	def set(self, year: int, month: int, day: int) -> None:
		"""SYSTem:DATE \n
		Snippet: driver.system.date.set(year = 1, month = 1, day = 1) \n
		Sets the date of the internal calendar. \n
			:param year: Year, to be entered as a four-digit number (including the century and millennium information)
			:param month: Month, 1 (January) to 12 (December)
			:param day: Day, 1 to the maximum number of days in the specified month
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('year', year, DataType.Integer), ArgSingle('month', month, DataType.Integer), ArgSingle('day', day, DataType.Integer))
		self._core.io.write(f'SYSTem:DATE {param}'.rstrip())

	# noinspection PyTypeChecker
	class DateStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Year: int: Year, to be entered as a four-digit number (including the century and millennium information)
			- 2 Month: int: Month, 1 (January) to 12 (December)
			- 3 Day: int: Day, 1 to the maximum number of days in the specified month"""
		__meta_args_list = [
			ArgStruct.scalar_int('Year'),
			ArgStruct.scalar_int('Month'),
			ArgStruct.scalar_int('Day')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Year: int = None
			self.Month: int = None
			self.Day: int = None

	def get(self) -> DateStruct:
		"""SYSTem:DATE \n
		Snippet: value: DateStruct = driver.system.date.get() \n
		Sets the date of the internal calendar. \n
			:return: structure: for return value, see the help for DateStruct structure arguments."""
		return self._core.io.query_struct(f'SYSTem:DATE?', self.__class__.DateStruct())
