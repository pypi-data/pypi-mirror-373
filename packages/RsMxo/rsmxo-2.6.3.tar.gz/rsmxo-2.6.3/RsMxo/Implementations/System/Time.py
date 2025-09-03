from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Types import DataType
from ...Internal.StructBase import StructBase
from ...Internal.ArgStruct import ArgStruct
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimeCls:
	"""Time commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def set(self, hours: int, minutes: int, seconds: int) -> None:
		"""SYSTem:TIME \n
		Snippet: driver.system.time.set(hours = 1, minutes = 1, seconds = 1) \n
		Returns the current time of the clock. \n
			:param hours: No help available
			:param minutes: No help available
			:param seconds: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('hours', hours, DataType.Integer), ArgSingle('minutes', minutes, DataType.Integer), ArgSingle('seconds', seconds, DataType.Integer))
		self._core.io.write(f'SYSTem:TIME {param}'.rstrip())

	# noinspection PyTypeChecker
	class TimeStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Hours: int: No parameter help available
			- 2 Minutes: int: No parameter help available
			- 3 Seconds: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Hours'),
			ArgStruct.scalar_int('Minutes'),
			ArgStruct.scalar_int('Seconds')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Hours: int = None
			self.Minutes: int = None
			self.Seconds: int = None

	def get(self) -> TimeStruct:
		"""SYSTem:TIME \n
		Snippet: value: TimeStruct = driver.system.time.get() \n
		Returns the current time of the clock. \n
			:return: structure: for return value, see the help for TimeStruct structure arguments."""
		return self._core.io.query_struct(f'SYSTem:TIME?', self.__class__.TimeStruct())
