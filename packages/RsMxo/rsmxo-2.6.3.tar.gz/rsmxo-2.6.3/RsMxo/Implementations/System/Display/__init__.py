from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DisplayCls:
	"""Display commands group definition. 3 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("display", core, parent)

	@property
	def message(self):
		"""message commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_message'):
			from .Message import MessageCls
			self._message = MessageCls(self._core, self._cmd_group)
		return self._message

	def get_update(self) -> bool:
		"""SYSTem:DISPlay:UPDate \n
		Snippet: value: bool = driver.system.display.get_update() \n
		Defines whether the display is updated while the instrument is in the remote state. If the display is switched off, the
		normal GUI is replaced by a static image while the instrument is in the remote state. Switching off the display can speed
		up the measurement. OFF is the recommended state. \n
			:return: display_update: ON| 1: The display is shown and updated during remote control. OFF| 0: The display shows a static image during remote control.
		"""
		response = self._core.io.query_str('SYSTem:DISPlay:UPDate?')
		return Conversions.str_to_bool(response)

	def set_update(self, display_update: bool) -> None:
		"""SYSTem:DISPlay:UPDate \n
		Snippet: driver.system.display.set_update(display_update = False) \n
		Defines whether the display is updated while the instrument is in the remote state. If the display is switched off, the
		normal GUI is replaced by a static image while the instrument is in the remote state. Switching off the display can speed
		up the measurement. OFF is the recommended state. \n
			:param display_update: ON| 1: The display is shown and updated during remote control. OFF| 0: The display shows a static image during remote control.
		"""
		param = Conversions.bool_to_str(display_update)
		self._core.io.write(f'SYSTem:DISPlay:UPDate {param}')

	def clone(self) -> 'DisplayCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DisplayCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
