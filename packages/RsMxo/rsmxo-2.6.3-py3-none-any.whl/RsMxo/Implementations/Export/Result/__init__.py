from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 8 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	@property
	def select(self):
		"""select commands group. 2 Sub-classes, 2 commands."""
		if not hasattr(self, '_select'):
			from .Select import SelectCls
			self._select = SelectCls(self._core, self._cmd_group)
		return self._select

	def save(self) -> None:
		"""EXPort:RESult:SAVE \n
		Snippet: driver.export.result.save() \n
		Saves the results to file. The target file is set using method RsMxo.Export.Result.name. To select the results to be
		exported, use method RsMxo.Export.Result.Select.cursor and method RsMxo.Export.Result.Select.measurement. \n
		"""
		self._core.io.write(f'EXPort:RESult:SAVE')

	def save_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""EXPort:RESult:SAVE \n
		Snippet: driver.export.result.save_and_wait() \n
		Saves the results to file. The target file is set using method RsMxo.Export.Result.name. To select the results to be
		exported, use method RsMxo.Export.Result.Select.cursor and method RsMxo.Export.Result.Select.measurement. \n
		Same as save, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'EXPort:RESult:SAVE', opc_timeout_ms)

	def get_name(self) -> str:
		"""EXPort:RESult:NAME \n
		Snippet: value: str = driver.export.result.get_name() \n
		Sets the path, the filename and the file format of the export file. \n
			:return: file_path: String with path and file name with extension .csv.
		"""
		response = self._core.io.query_str('EXPort:RESult:NAME?')
		return trim_str_response(response)

	def set_name(self, file_path: str) -> None:
		"""EXPort:RESult:NAME \n
		Snippet: driver.export.result.set_name(file_path = 'abc') \n
		Sets the path, the filename and the file format of the export file. \n
			:param file_path: String with path and file name with extension .csv.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'EXPort:RESult:NAME {param}')

	def clone(self) -> 'ResultCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ResultCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
