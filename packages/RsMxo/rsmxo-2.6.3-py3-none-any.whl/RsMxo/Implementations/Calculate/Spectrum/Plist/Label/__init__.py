from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 5 total commands, 5 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	@property
	def maxCount(self):
		"""maxCount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_maxCount'):
			from .MaxCount import MaxCountCls
			self._maxCount = MaxCountCls(self._core, self._cmd_group)
		return self._maxCount

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def invert(self):
		"""invert commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_invert'):
			from .Invert import InvertCls
			self._invert = InvertCls(self._core, self._cmd_group)
		return self._invert

	@property
	def border(self):
		"""border commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_border'):
			from .Border import BorderCls
			self._border = BorderCls(self._core, self._cmd_group)
		return self._border

	@property
	def frequency(self):
		"""frequency commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	def clone(self) -> 'LabelCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = LabelCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
