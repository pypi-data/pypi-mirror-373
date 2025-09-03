from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class InvertCls:
	"""Invert commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("invert", core, parent)

	def set(self) -> None:
		"""TRIGger:SBSW:NRZC:INVert \n
		Snippet: driver.trigger.sbsw.nrzc.invert.set() \n
		Inverts the current state of the frame and error types for the software trigger: all frames and error types that were
		enabled are disabled and vice versa. \n
		"""
		self._core.io.write(f'TRIGger:SBSW:NRZC:INVert')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""TRIGger:SBSW:NRZC:INVert \n
		Snippet: driver.trigger.sbsw.nrzc.invert.set_and_wait() \n
		Inverts the current state of the frame and error types for the software trigger: all frames and error types that were
		enabled are disabled and vice versa. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'TRIGger:SBSW:NRZC:INVert', opc_timeout_ms)
