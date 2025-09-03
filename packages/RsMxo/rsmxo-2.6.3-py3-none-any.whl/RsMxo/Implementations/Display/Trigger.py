from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TriggerCls:
	"""Trigger commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("trigger", core, parent)

	def get_lines(self) -> bool:
		"""DISPlay:TRIGger:LINes \n
		Snippet: value: bool = driver.display.trigger.get_lines() \n
		No command help available \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('DISPlay:TRIGger:LINes?')
		return Conversions.str_to_bool(response)

	def set_lines(self, state: bool) -> None:
		"""DISPlay:TRIGger:LINes \n
		Snippet: driver.display.trigger.set_lines(state = False) \n
		No command help available \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'DISPlay:TRIGger:LINes {param}')
