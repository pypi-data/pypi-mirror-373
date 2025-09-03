from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ApointCls:
	"""Apoint commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("apoint", core, parent)

	def set(self) -> None:
		"""FRANalysis:AMPLitude:PROFile:APOint \n
		Snippet: driver.franalysis.amplitude.profile.apoint.set() \n
		Adds a new point to the amplitude profile. \n
		"""
		self._core.io.write(f'FRANalysis:AMPLitude:PROFile:APOint')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""FRANalysis:AMPLitude:PROFile:APOint \n
		Snippet: driver.franalysis.amplitude.profile.apoint.set_and_wait() \n
		Adds a new point to the amplitude profile. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'FRANalysis:AMPLitude:PROFile:APOint', opc_timeout_ms)
