from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StatisticsCls:
	"""Statistics commands group definition. 3 total commands, 2 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("statistics", core, parent)

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def areset(self):
		"""areset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_areset'):
			from .Areset import AresetCls
			self._areset = AresetCls(self._core, self._cmd_group)
		return self._areset

	def reset(self, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:STATistics:RESet \n
		Snippet: driver.measurement.statistics.reset(measIndex = repcap.MeasIndex.Default) \n
		Resets the statistics for all measurements. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:STATistics:RESet')

	def reset_and_wait(self, measIndex=repcap.MeasIndex.Default, opc_timeout_ms: int = -1) -> None:
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		"""MEASurement<*>:STATistics:RESet \n
		Snippet: driver.measurement.statistics.reset_and_wait(measIndex = repcap.MeasIndex.Default) \n
		Resets the statistics for all measurements. \n
		Same as reset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MEASurement{measIndex_cmd_val}:STATistics:RESet', opc_timeout_ms)

	def clone(self) -> 'StatisticsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = StatisticsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
