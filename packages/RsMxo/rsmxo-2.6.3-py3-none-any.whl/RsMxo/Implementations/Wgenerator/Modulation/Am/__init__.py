from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AmCls:
	"""Am commands group definition. 5 total commands, 5 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("am", core, parent)

	@property
	def function(self):
		"""function commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_function'):
			from .Function import FunctionCls
			self._function = FunctionCls(self._core, self._cmd_group)
		return self._function

	@property
	def dcycle(self):
		"""dcycle commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dcycle'):
			from .Dcycle import DcycleCls
			self._dcycle = DcycleCls(self._core, self._cmd_group)
		return self._dcycle

	@property
	def symmetry(self):
		"""symmetry commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symmetry'):
			from .Symmetry import SymmetryCls
			self._symmetry = SymmetryCls(self._core, self._cmd_group)
		return self._symmetry

	@property
	def frequency(self):
		"""frequency commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def depth(self):
		"""depth commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_depth'):
			from .Depth import DepthCls
			self._depth = DepthCls(self._core, self._cmd_group)
		return self._depth

	def clone(self) -> 'AmCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AmCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
