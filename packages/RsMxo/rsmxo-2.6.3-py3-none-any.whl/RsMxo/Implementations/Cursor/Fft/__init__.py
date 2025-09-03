from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FftCls:
	"""Fft commands group definition. 2 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fft", core, parent)

	@property
	def toCenter(self):
		"""toCenter commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_toCenter'):
			from .ToCenter import ToCenterCls
			self._toCenter = ToCenterCls(self._core, self._cmd_group)
		return self._toCenter

	@property
	def setCenter(self):
		"""setCenter commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_setCenter'):
			from .SetCenter import SetCenterCls
			self._setCenter = SetCenterCls(self._core, self._cmd_group)
		return self._setCenter

	def clone(self) -> 'FftCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FftCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
