from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


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
	def wfmCount(self):
		"""wfmCount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_wfmCount'):
			from .WfmCount import WfmCountCls
			self._wfmCount = WfmCountCls(self._core, self._cmd_group)
		return self._wfmCount

	def reset(self, power=repcap.Power.Default) -> None:
		"""POWer<*>:SWITching:STATistics:RESet \n
		Snippet: driver.power.switching.statistics.reset(power = repcap.Power.Default) \n
		Resets the statistic calculation for all power measurements that use statistics. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:SWITching:STATistics:RESet')

	def reset_and_wait(self, power=repcap.Power.Default, opc_timeout_ms: int = -1) -> None:
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		"""POWer<*>:SWITching:STATistics:RESet \n
		Snippet: driver.power.switching.statistics.reset_and_wait(power = repcap.Power.Default) \n
		Resets the statistic calculation for all power measurements that use statistics. \n
		Same as reset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'POWer{power_cmd_val}:SWITching:STATistics:RESet', opc_timeout_ms)

	def clone(self) -> 'StatisticsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = StatisticsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
