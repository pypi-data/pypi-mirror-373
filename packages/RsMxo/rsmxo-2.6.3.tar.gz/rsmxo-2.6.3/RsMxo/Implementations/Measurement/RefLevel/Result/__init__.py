from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 5 total commands, 5 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	@property
	def lower(self):
		"""lower commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_lower'):
			from .Lower import LowerCls
			self._lower = LowerCls(self._core, self._cmd_group)
		return self._lower

	@property
	def middle(self):
		"""middle commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_middle'):
			from .Middle import MiddleCls
			self._middle = MiddleCls(self._core, self._cmd_group)
		return self._middle

	@property
	def sigHigh(self):
		"""sigHigh commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sigHigh'):
			from .SigHigh import SigHighCls
			self._sigHigh = SigHighCls(self._core, self._cmd_group)
		return self._sigHigh

	@property
	def sigLow(self):
		"""sigLow commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sigLow'):
			from .SigLow import SigLowCls
			self._sigLow = SigLowCls(self._core, self._cmd_group)
		return self._sigLow

	@property
	def upper(self):
		"""upper commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_upper'):
			from .Upper import UpperCls
			self._upper = UpperCls(self._core, self._cmd_group)
		return self._upper

	def clone(self) -> 'ResultCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ResultCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
