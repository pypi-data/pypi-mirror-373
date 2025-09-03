from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StatusCls:
	"""Status commands group definition. 5 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("status", core, parent)

	@property
	def operation(self):
		"""operation commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_operation'):
			from .Operation import OperationCls
			self._operation = OperationCls(self._core, self._cmd_group)
		return self._operation

	def preset(self) -> None:
		"""STATus:PRESet \n
		Snippet: driver.status.preset() \n
		Resets the status registers. All PTRansition bits are set to 1, i.e. all transitions from 0 to 1 are detected.
		All NTRansition bits are set to 0, i.e. a transition from 1 to 0 in a CONDition bit is not detected. All EVENt bits are
		set to 0. The ENABle bits of method RsMxo.Status.Operation.event and STATus:QUEStionable are set to 0, i.e. all events in
		these registers are not passed on. \n
		"""
		self._core.io.write(f'STATus:PRESet')

	def preset_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""STATus:PRESet \n
		Snippet: driver.status.preset_and_wait() \n
		Resets the status registers. All PTRansition bits are set to 1, i.e. all transitions from 0 to 1 are detected.
		All NTRansition bits are set to 0, i.e. a transition from 1 to 0 in a CONDition bit is not detected. All EVENt bits are
		set to 0. The ENABle bits of method RsMxo.Status.Operation.event and STATus:QUEStionable are set to 0, i.e. all events in
		these registers are not passed on. \n
		Same as preset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'STATus:PRESet', opc_timeout_ms)

	def clone(self) -> 'StatusCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = StatusCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
