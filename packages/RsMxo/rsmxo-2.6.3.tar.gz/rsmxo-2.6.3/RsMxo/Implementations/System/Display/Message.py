from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MessageCls:
	"""Message commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("message", core, parent)

	def get_text(self) -> str:
		"""SYSTem:DISPlay:MESSage[:TEXT] \n
		Snippet: value: str = driver.system.display.message.get_text() \n
		Defines an additional text that is displayed during remote control operation. To enable the text display, use method
		RsMxo.System.Display.Message.state. \n
			:return: display_message: No help available
		"""
		response = self._core.io.query_str('SYSTem:DISPlay:MESSage:TEXT?')
		return trim_str_response(response)

	def set_text(self, display_message: str) -> None:
		"""SYSTem:DISPlay:MESSage[:TEXT] \n
		Snippet: driver.system.display.message.set_text(display_message = 'abc') \n
		Defines an additional text that is displayed during remote control operation. To enable the text display, use method
		RsMxo.System.Display.Message.state. \n
			:param display_message: No help available
		"""
		param = Conversions.value_to_quoted_str(display_message)
		self._core.io.write(f'SYSTem:DISPlay:MESSage:TEXT {param}')

	def get_state(self) -> bool:
		"""SYSTem:DISPlay:MESSage:STATe \n
		Snippet: value: bool = driver.system.display.message.get_state() \n
		Enables and disables the display of an additional text in remote control. To define the text, use method RsMxo.System.
		Display.Message.text. \n
			:return: disp_mess_st: No help available
		"""
		response = self._core.io.query_str('SYSTem:DISPlay:MESSage:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, disp_mess_st: bool) -> None:
		"""SYSTem:DISPlay:MESSage:STATe \n
		Snippet: driver.system.display.message.set_state(disp_mess_st = False) \n
		Enables and disables the display of an additional text in remote control. To define the text, use method RsMxo.System.
		Display.Message.text. \n
			:param disp_mess_st: No help available
		"""
		param = Conversions.bool_to_str(disp_mess_st)
		self._core.io.write(f'SYSTem:DISPlay:MESSage:STATe {param}')
