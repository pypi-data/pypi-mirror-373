from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DeviceCls:
	"""Device commands group definition. 10 total commands, 9 Subgroups, 0 group commands
	Repeated Capability: Device, default value after init: Device.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("device", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_device_get', 'repcap_device_set', repcap.Device.Nr1)

	def repcap_device_set(self, device: repcap.Device) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Device.Default.
		Default value after init: Device.Nr1"""
		self._cmd_group.set_repcap_enum_value(device)

	def repcap_device_get(self) -> repcap.Device:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	@property
	def connect(self):
		"""connect commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_connect'):
			from .Connect import ConnectCls
			self._connect = ConnectCls(self._core, self._cmd_group)
		return self._connect

	@property
	def channels(self):
		"""channels commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_channels'):
			from .Channels import ChannelsCls
			self._channels = ChannelsCls(self._core, self._cmd_group)
		return self._channels

	@property
	def timeBaseSync(self):
		"""timeBaseSync commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_timeBaseSync'):
			from .TimeBaseSync import TimeBaseSyncCls
			self._timeBaseSync = TimeBaseSyncCls(self._core, self._cmd_group)
		return self._timeBaseSync

	@property
	def lockControls(self):
		"""lockControls commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_lockControls'):
			from .LockControls import LockControlsCls
			self._lockControls = LockControlsCls(self._core, self._cmd_group)
		return self._lockControls

	@property
	def display(self):
		"""display commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def skew(self):
		"""skew commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_skew'):
			from .Skew import SkewCls
			self._skew = SkewCls(self._core, self._cmd_group)
		return self._skew

	@property
	def communicate(self):
		"""communicate commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_communicate'):
			from .Communicate import CommunicateCls
			self._communicate = CommunicateCls(self._core, self._cmd_group)
		return self._communicate

	def clone(self) -> 'DeviceCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DeviceCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
