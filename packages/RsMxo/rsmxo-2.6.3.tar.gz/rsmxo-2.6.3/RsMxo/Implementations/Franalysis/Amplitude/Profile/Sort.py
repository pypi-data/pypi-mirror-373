from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SortCls:
	"""Sort commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sort", core, parent)

	def set(self) -> None:
		"""FRANalysis:AMPLitude:PROFile:SORT \n
		Snippet: driver.franalysis.amplitude.profile.sort.set() \n
		Sorts the points in the amplitude table by frequency, starting with the lowest frequency. \n
		"""
		self._core.io.write(f'FRANalysis:AMPLitude:PROFile:SORT')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""FRANalysis:AMPLitude:PROFile:SORT \n
		Snippet: driver.franalysis.amplitude.profile.sort.set_and_wait() \n
		Sorts the points in the amplitude table by frequency, starting with the lowest frequency. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'FRANalysis:AMPLitude:PROFile:SORT', opc_timeout_ms)
