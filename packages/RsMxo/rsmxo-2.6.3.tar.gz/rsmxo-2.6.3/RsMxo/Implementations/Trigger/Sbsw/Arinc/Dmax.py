from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Types import DataType
from .....Internal.Utilities import trim_str_response
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DmaxCls:
	"""Dmax commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmax", core, parent)

	def set(self, frame: str, field: str, data: str) -> None:
		"""TRIGger:SBSW:ARINc:DMAX \n
		Snippet: driver.trigger.sbsw.arinc.dmax.set(frame = 'abc', field = 'abc', data = 'abc') \n
		Sets the end value of a data pattern range for the software trigger, if the operator is set to INRange or OORANGe.
		You can set the operator with method RsMxo.Trigger.Sbsw.Arinc.Frame.Fld.Doperator.set. \n
			:param frame: No help available
			:param field: No help available
			:param data: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('data', data, DataType.String))
		self._core.io.write(f'TRIGger:SBSW:ARINc:DMAX {param}'.rstrip())

	def get(self) -> str:
		"""TRIGger:SBSW:ARINc:DMAX \n
		Snippet: value: str = driver.trigger.sbsw.arinc.dmax.get() \n
		Sets the end value of a data pattern range for the software trigger, if the operator is set to INRange or OORANGe.
		You can set the operator with method RsMxo.Trigger.Sbsw.Arinc.Frame.Fld.Doperator.set. \n
			:return: data: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:ARINc:DMAX?')
		return trim_str_response(response)
