from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FindLevelCls:
	"""FindLevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("findLevel", core, parent)

	def set(self) -> None:
		"""TRIGger:FINDlevel \n
		Snippet: driver.trigger.findLevel.set() \n
		Sets the trigger level automatically to 0.5 * (MaxPeak – MinPeak) . In a trigger sequence, Find level affects all active
		events of the sequence (A, B, and R event) . \n
		"""
		self._core.io.write(f'TRIGger:FINDlevel')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""TRIGger:FINDlevel \n
		Snippet: driver.trigger.findLevel.set_and_wait() \n
		Sets the trigger level automatically to 0.5 * (MaxPeak – MinPeak) . In a trigger sequence, Find level affects all active
		events of the sequence (A, B, and R event) . \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'TRIGger:FINDlevel', opc_timeout_ms)
