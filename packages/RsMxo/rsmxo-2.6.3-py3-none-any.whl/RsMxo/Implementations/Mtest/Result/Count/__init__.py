from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 3 total commands, 3 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	@property
	def waveforms(self):
		"""waveforms commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_waveforms'):
			from .Waveforms import WaveformsCls
			self._waveforms = WaveformsCls(self._core, self._cmd_group)
		return self._waveforms

	@property
	def fwaveforms(self):
		"""fwaveforms commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fwaveforms'):
			from .Fwaveforms import FwaveformsCls
			self._fwaveforms = FwaveformsCls(self._core, self._cmd_group)
		return self._fwaveforms

	@property
	def pwaveforms(self):
		"""pwaveforms commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pwaveforms'):
			from .Pwaveforms import PwaveformsCls
			self._pwaveforms = PwaveformsCls(self._core, self._cmd_group)
		return self._pwaveforms

	def clone(self) -> 'CountCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CountCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
