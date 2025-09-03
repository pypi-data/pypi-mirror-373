from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HorizontalCls:
	"""Horizontal commands group definition. 1 total commands, 1 Subgroups, 0 group commands
	Repeated Capability: Horizontal, default value after init: Horizontal.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("horizontal", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_horizontal_get', 'repcap_horizontal_set', repcap.Horizontal.Nr1)

	def repcap_horizontal_set(self, horizontal: repcap.Horizontal) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Horizontal.Default.
		Default value after init: Horizontal.Nr1"""
		self._cmd_group.set_repcap_enum_value(horizontal)

	def repcap_horizontal_get(self) -> repcap.Horizontal:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def label(self):
		"""label commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_label'):
			from .Label import LabelCls
			self._label = LabelCls(self._core, self._cmd_group)
		return self._label

	def clone(self) -> 'HorizontalCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = HorizontalCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
