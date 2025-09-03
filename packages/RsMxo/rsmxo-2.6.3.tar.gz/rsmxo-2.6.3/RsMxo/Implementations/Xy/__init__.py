from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class XyCls:
	"""Xy commands group definition. 4 total commands, 4 Subgroups, 0 group commands
	Repeated Capability: XyAxis, default value after init: XyAxis.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xy", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_xyAxis_get', 'repcap_xyAxis_set', repcap.XyAxis.Nr1)

	def repcap_xyAxis_set(self, xyAxis: repcap.XyAxis) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to XyAxis.Default.
		Default value after init: XyAxis.Nr1"""
		self._cmd_group.set_repcap_enum_value(xyAxis)

	def repcap_xyAxis_get(self) -> repcap.XyAxis:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def swap(self):
		"""swap commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_swap'):
			from .Swap import SwapCls
			self._swap = SwapCls(self._core, self._cmd_group)
		return self._swap

	@property
	def xsource(self):
		"""xsource commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_xsource'):
			from .Xsource import XsourceCls
			self._xsource = XsourceCls(self._core, self._cmd_group)
		return self._xsource

	@property
	def ysource(self):
		"""ysource commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ysource'):
			from .Ysource import YsourceCls
			self._ysource = YsourceCls(self._core, self._cmd_group)
		return self._ysource

	def clone(self) -> 'XyCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = XyCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
