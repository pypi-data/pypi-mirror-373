from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal.RepeatedCapability import RepeatedCapability
from ........ import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ChanCls:
	"""Chan commands group definition. 1 total commands, 1 Subgroups, 0 group commands
	Repeated Capability: ChannelDigital, default value after init: ChannelDigital.DigCh1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("chan", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_channelDigital_get', 'repcap_channelDigital_set', repcap.ChannelDigital.DigCh1)

	def repcap_channelDigital_set(self, channelDigital: repcap.ChannelDigital) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to ChannelDigital.Default.
		Default value after init: ChannelDigital.DigCh1"""
		self._cmd_group.set_repcap_enum_value(channelDigital)

	def repcap_channelDigital_get(self) -> repcap.ChannelDigital:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def hlx(self):
		"""hlx commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_hlx'):
			from .Hlx import HlxCls
			self._hlx = HlxCls(self._core, self._cmd_group)
		return self._hlx

	def clone(self) -> 'ChanCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ChanCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
