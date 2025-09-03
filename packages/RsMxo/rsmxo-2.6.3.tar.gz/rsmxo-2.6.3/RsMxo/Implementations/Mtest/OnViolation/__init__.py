from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OnViolationCls:
	"""OnViolation commands group definition. 6 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("onViolation", core, parent)

	@property
	def beep(self):
		"""beep commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_beep'):
			from .Beep import BeepCls
			self._beep = BeepCls(self._core, self._cmd_group)
		return self._beep

	@property
	def stop(self):
		"""stop commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stop'):
			from .Stop import StopCls
			self._stop = StopCls(self._core, self._cmd_group)
		return self._stop

	@property
	def wfmSave(self):
		"""wfmSave commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_wfmSave'):
			from .WfmSave import WfmSaveCls
			self._wfmSave = WfmSaveCls(self._core, self._cmd_group)
		return self._wfmSave

	@property
	def triggerOut(self):
		"""triggerOut commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_triggerOut'):
			from .TriggerOut import TriggerOutCls
			self._triggerOut = TriggerOutCls(self._core, self._cmd_group)
		return self._triggerOut

	@property
	def screenshot(self):
		"""screenshot commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_screenshot'):
			from .Screenshot import ScreenshotCls
			self._screenshot = ScreenshotCls(self._core, self._cmd_group)
		return self._screenshot

	@property
	def srefCurve(self):
		"""srefCurve commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_srefCurve'):
			from .SrefCurve import SrefCurveCls
			self._srefCurve = SrefCurveCls(self._core, self._cmd_group)
		return self._srefCurve

	def clone(self) -> 'OnViolationCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = OnViolationCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
