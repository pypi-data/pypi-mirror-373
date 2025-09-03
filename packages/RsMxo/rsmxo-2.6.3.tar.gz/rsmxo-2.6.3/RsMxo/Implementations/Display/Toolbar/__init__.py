from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ToolbarCls:
	"""Toolbar commands group definition. 3 total commands, 2 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("toolbar", core, parent)

	@property
	def deselect(self):
		"""deselect commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_deselect'):
			from .Deselect import DeselectCls
			self._deselect = DeselectCls(self._core, self._cmd_group)
		return self._deselect

	@property
	def restore(self):
		"""restore commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_restore'):
			from .Restore import RestoreCls
			self._restore = RestoreCls(self._core, self._cmd_group)
		return self._restore

	def get_count(self) -> int:
		"""DISPlay:TOOLbar:COUNt \n
		Snippet: value: int = driver.display.toolbar.get_count() \n
		Returns the number of tools that are currently assigned to the toolbar. \n
			:return: tool_count: No help available
		"""
		response = self._core.io.query_str('DISPlay:TOOLbar:COUNt?')
		return Conversions.str_to_int(response)

	def clone(self) -> 'ToolbarCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ToolbarCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
