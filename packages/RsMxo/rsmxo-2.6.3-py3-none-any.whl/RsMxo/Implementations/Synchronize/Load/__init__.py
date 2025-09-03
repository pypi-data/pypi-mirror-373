from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LoadCls:
	"""Load commands group definition. 3 total commands, 2 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("load", core, parent)

	@property
	def sessions(self):
		"""sessions commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sessions'):
			from .Sessions import SessionsCls
			self._sessions = SessionsCls(self._core, self._cmd_group)
		return self._sessions

	@property
	def waveform(self):
		"""waveform commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_waveform'):
			from .Waveform import WaveformCls
			self._waveform = WaveformCls(self._core, self._cmd_group)
		return self._waveform

	def abort(self) -> None:
		"""SYNChronize:LOAD:ABORt \n
		Snippet: driver.synchronize.load.abort() \n
		No command help available \n
		"""
		self._core.io.write(f'SYNChronize:LOAD:ABORt')

	def abort_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""SYNChronize:LOAD:ABORt \n
		Snippet: driver.synchronize.load.abort_and_wait() \n
		No command help available \n
		Same as abort, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SYNChronize:LOAD:ABORt', opc_timeout_ms)

	def clone(self) -> 'LoadCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = LoadCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
