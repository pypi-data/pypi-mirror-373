from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BacklightCls:
	"""Backlight commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("backlight", core, parent)

	def get_brigtness(self) -> int:
		"""DISPlay:BACKlight[:BRIGtness] \n
		Snippet: value: int = driver.display.backlight.get_brigtness() \n
		Sets the background luminosity of the touchscreen. \n
			:return: lcd_intensity: No help available
		"""
		response = self._core.io.query_str('DISPlay:BACKlight:BRIGtness?')
		return Conversions.str_to_int(response)

	def set_brigtness(self, lcd_intensity: int) -> None:
		"""DISPlay:BACKlight[:BRIGtness] \n
		Snippet: driver.display.backlight.set_brigtness(lcd_intensity = 1) \n
		Sets the background luminosity of the touchscreen. \n
			:param lcd_intensity: No help available
		"""
		param = Conversions.decimal_value_to_str(lcd_intensity)
		self._core.io.write(f'DISPlay:BACKlight:BRIGtness {param}')

	# noinspection PyTypeChecker
	def get_dimming(self) -> enums.UserActivityTout:
		"""DISPlay:BACKlight:DIMMing \n
		Snippet: value: enums.UserActivityTout = driver.display.backlight.get_dimming() \n
		Selects a time, after which the monitor brightness is reduced, if the instrument was inactive. Remote control of the
		instrument is also considered as an activity. \n
			:return: usr_activity_tout: No help available
		"""
		response = self._core.io.query_str('DISPlay:BACKlight:DIMMing?')
		return Conversions.str_to_scalar_enum(response, enums.UserActivityTout)

	def set_dimming(self, usr_activity_tout: enums.UserActivityTout) -> None:
		"""DISPlay:BACKlight:DIMMing \n
		Snippet: driver.display.backlight.set_dimming(usr_activity_tout = enums.UserActivityTout.OFF) \n
		Selects a time, after which the monitor brightness is reduced, if the instrument was inactive. Remote control of the
		instrument is also considered as an activity. \n
			:param usr_activity_tout: No help available
		"""
		param = Conversions.enum_scalar_to_str(usr_activity_tout, enums.UserActivityTout)
		self._core.io.write(f'DISPlay:BACKlight:DIMMing {param}')
