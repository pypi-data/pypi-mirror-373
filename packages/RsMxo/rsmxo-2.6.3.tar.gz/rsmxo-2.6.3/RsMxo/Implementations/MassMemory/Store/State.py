from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Types import DataType
from ....Internal.ArgSingleList import ArgSingleList
from ....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, memory_number: int, file_path: str) -> None:
		"""MMEMory:STORe:STATe \n
		Snippet: driver.massMemory.store.state.set(memory_number = 1, file_path = 'abc') \n
		Stores the instrument settings from the specified internal memory to the specified file. To store the current instrument
		settings to the internal memory, use *SAV first. \n
			:param memory_number: Number of the internal memory
			:param file_path: String parameter specifying the complete path and filename of the source file.
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('memory_number', memory_number, DataType.Integer), ArgSingle('file_path', file_path, DataType.String))
		self._core.io.write_with_opc(f'MMEMory:STORe:STATe {param}'.rstrip())
