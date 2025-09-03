from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CalculateCls:
	"""Calculate commands group definition. 70 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("calculate", core, parent)

	@property
	def math(self):
		"""math commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_math'):
			from .Math import MathCls
			self._math = MathCls(self._core, self._cmd_group)
		return self._math

	@property
	def spectrum(self):
		"""spectrum commands group. 10 Sub-classes, 1 commands."""
		if not hasattr(self, '_spectrum'):
			from .Spectrum import SpectrumCls
			self._spectrum = SpectrumCls(self._core, self._cmd_group)
		return self._spectrum

	def clone(self) -> 'CalculateCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CalculateCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
