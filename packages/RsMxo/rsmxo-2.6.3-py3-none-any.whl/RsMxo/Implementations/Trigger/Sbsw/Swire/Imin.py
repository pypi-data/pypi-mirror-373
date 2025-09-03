from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IminCls:
	"""Imin commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("imin", core, parent)

	def set(self, frame: str, field: str, data: int) -> None:
		"""TRIGger:SBSW:SWIRe:IMIN \n
		Snippet: driver.trigger.sbsw.swire.imin.set(frame = 'abc', field = 'abc', data = 1) \n
		No command help available \n
			:param frame: No help available
			:param field: No help available
			:param data: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('data', data, DataType.Integer))
		self._core.io.write(f'TRIGger:SBSW:SWIRe:IMIN {param}'.rstrip())

	def get(self) -> int:
		"""TRIGger:SBSW:SWIRe:IMIN \n
		Snippet: value: int = driver.trigger.sbsw.swire.imin.get() \n
		No command help available \n
			:return: data: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:SWIRe:IMIN?')
		return Conversions.str_to_int(response)
