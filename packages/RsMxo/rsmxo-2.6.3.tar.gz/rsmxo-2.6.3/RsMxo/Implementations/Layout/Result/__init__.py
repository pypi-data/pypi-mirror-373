from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 2 total commands, 2 Subgroups, 0 group commands
	Repeated Capability: Result, default value after init: Result.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_result_get', 'repcap_result_set', repcap.Result.Nr1)

	def repcap_result_set(self, result: repcap.Result) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Result.Default.
		Default value after init: Result.Nr1"""
		self._cmd_group.set_repcap_enum_value(result)

	def repcap_result_get(self) -> repcap.Result:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def horizontal(self):
		"""horizontal commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_horizontal'):
			from .Horizontal import HorizontalCls
			self._horizontal = HorizontalCls(self._core, self._cmd_group)
		return self._horizontal

	@property
	def vertical(self):
		"""vertical commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_vertical'):
			from .Vertical import VerticalCls
			self._vertical = VerticalCls(self._core, self._cmd_group)
		return self._vertical

	def clone(self) -> 'ResultCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ResultCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
