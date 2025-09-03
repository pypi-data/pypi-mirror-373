from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.RepeatedCapability import RepeatedCapability
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class XdataCls:
	"""Xdata commands group definition. 6 total commands, 6 Subgroups, 0 group commands
	Repeated Capability: Xdata, default value after init: Xdata.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xdata", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_xdata_get', 'repcap_xdata_set', repcap.Xdata.Nr1)

	def repcap_xdata_set(self, xdata: repcap.Xdata) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Xdata.Default.
		Default value after init: Xdata.Nr1"""
		self._cmd_group.set_repcap_enum_value(xdata)

	def repcap_xdata_get(self) -> repcap.Xdata:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def sdt(self):
		"""sdt commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sdt'):
			from .Sdt import SdtCls
			self._sdt = SdtCls(self._core, self._cmd_group)
		return self._sdt

	@property
	def sec(self):
		"""sec commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sec'):
			from .Sec import SecCls
			self._sec = SecCls(self._core, self._cmd_group)
		return self._sec

	@property
	def pcRc(self):
		"""pcRc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pcRc'):
			from .PcRc import PcRcCls
			self._pcRc = PcRcCls(self._core, self._cmd_group)
		return self._pcRc

	@property
	def fcRc(self):
		"""fcRc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcRc'):
			from .FcRc import FcRcCls
			self._fcRc = FcRcCls(self._core, self._cmd_group)
		return self._fcRc

	@property
	def vcid(self):
		"""vcid commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_vcid'):
			from .Vcid import VcidCls
			self._vcid = VcidCls(self._core, self._cmd_group)
		return self._vcid

	@property
	def af(self):
		"""af commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_af'):
			from .Af import AfCls
			self._af = AfCls(self._core, self._cmd_group)
		return self._af

	def clone(self) -> 'XdataCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = XdataCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
