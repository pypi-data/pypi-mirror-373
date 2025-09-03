from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Types import DataType
from .....Internal.Utilities import trim_str_response
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DminCls:
	"""Dmin commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmin", core, parent)

	def set(self, frame: str, field: str, data: str) -> None:
		"""TRIGger:SBSW:MILStd:DMIN \n
		Snippet: driver.trigger.sbsw.milstd.dmin.set(frame = 'abc', field = 'abc', data = 'abc') \n
		Specifies the data pattern, or sets the start value of a data pattern range for the software trigger. \n
			:param frame: No help available
			:param field: No help available
			:param data: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('data', data, DataType.String))
		self._core.io.write(f'TRIGger:SBSW:MILStd:DMIN {param}'.rstrip())

	def get(self) -> str:
		"""TRIGger:SBSW:MILStd:DMIN \n
		Snippet: value: str = driver.trigger.sbsw.milstd.dmin.get() \n
		Specifies the data pattern, or sets the start value of a data pattern range for the software trigger. \n
			:return: data: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:MILStd:DMIN?')
		return trim_str_response(response)
