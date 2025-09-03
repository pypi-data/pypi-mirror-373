from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PlayCls:
	"""Play commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("play", core, parent)

	def set(self) -> None:
		"""ACQuire:HISTory:PLAY \n
		Snippet: driver.acquire.history.play.set() \n
		Starts and stops the replay of the history waveforms. \n
		"""
		self._core.io.write(f'ACQuire:HISTory:PLAY')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""ACQuire:HISTory:PLAY \n
		Snippet: driver.acquire.history.play.set_and_wait() \n
		Starts and stops the replay of the history waveforms. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'ACQuire:HISTory:PLAY', opc_timeout_ms)
