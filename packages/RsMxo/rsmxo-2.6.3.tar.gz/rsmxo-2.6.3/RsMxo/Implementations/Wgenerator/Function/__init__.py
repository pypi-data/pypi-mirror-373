from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FunctionCls:
	"""Function commands group definition. 4 total commands, 4 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("function", core, parent)

	@property
	def select(self):
		"""select commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_select'):
			from .Select import SelectCls
			self._select = SelectCls(self._core, self._cmd_group)
		return self._select

	@property
	def square(self):
		"""square commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_square'):
			from .Square import SquareCls
			self._square = SquareCls(self._core, self._cmd_group)
		return self._square

	@property
	def ramp(self):
		"""ramp commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_ramp'):
			from .Ramp import RampCls
			self._ramp = RampCls(self._core, self._cmd_group)
		return self._ramp

	@property
	def pulse(self):
		"""pulse commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_pulse'):
			from .Pulse import PulseCls
			self._pulse = PulseCls(self._core, self._cmd_group)
		return self._pulse

	def clone(self) -> 'FunctionCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FunctionCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
