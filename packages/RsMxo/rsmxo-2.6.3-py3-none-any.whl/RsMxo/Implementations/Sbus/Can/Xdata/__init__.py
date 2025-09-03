from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class XdataCls:
	"""Xdata commands group definition. 2 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xdata", core, parent)

	@property
	def dbitrate(self):
		"""dbitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dbitrate'):
			from .Dbitrate import DbitrateCls
			self._dbitrate = DbitrateCls(self._core, self._cmd_group)
		return self._dbitrate

	@property
	def samplePoint(self):
		"""samplePoint commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_samplePoint'):
			from .SamplePoint import SamplePointCls
			self._samplePoint = SamplePointCls(self._core, self._cmd_group)
		return self._samplePoint

	def clone(self) -> 'XdataCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = XdataCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
