from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SignalCls:
	"""Signal commands group definition. 4 total commands, 3 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("signal", core, parent)

	@property
	def assign(self):
		"""assign commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_assign'):
			from .Assign import AssignCls
			self._assign = AssignCls(self._core, self._cmd_group)
		return self._assign

	@property
	def use(self):
		"""use commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_use'):
			from .Use import UseCls
			self._use = UseCls(self._core, self._cmd_group)
		return self._use

	@property
	def color(self):
		"""color commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_color'):
			from .Color import ColorCls
			self._color = ColorCls(self._core, self._cmd_group)
		return self._color

	# noinspection PyTypeChecker
	def get_catalog(self) -> List[enums.ColorSignal]:
		"""DISPlay:COLor:SIGNal:Catalog \n
		Snippet: value: List[enums.ColorSignal] = driver.display.color.signal.get_catalog() \n
		Returns a list of valid signal names. The signal names are needed in other DISPlay:COLor commands to set the <Signal>
		parameter. \n
			:return: signals: Comma-separated list of signal names
		"""
		response = self._core.io.query_str('DISPlay:COLor:SIGNal:Catalog?')
		return Conversions.str_to_list_enum(response, enums.ColorSignal)

	def clone(self) -> 'SignalCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SignalCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
