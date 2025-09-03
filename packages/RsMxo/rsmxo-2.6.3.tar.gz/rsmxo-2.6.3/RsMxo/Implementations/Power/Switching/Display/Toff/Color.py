from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ColorCls:
	"""Color commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("color", core, parent)

	def set(self, turn_off_color: int, power=repcap.Power.Default) -> None:
		"""POWer<*>:SWITching:DISPlay:TOFF:COLor \n
		Snippet: driver.power.switching.display.toff.color.set(turn_off_color = 1, power = repcap.Power.Default) \n
		The commands set the display color of the conduction area, non-conduction area, turn off area and turn on area,
		respectively. \n
			:param turn_off_color: Decimal value of the ARGB color. Use the color dialog on the instrument to get the hex value of the color, and convert the hex value to a decimal value. 0 is fully transparent black. 4278190080 (dec) = FF000000 (hex) is opaque black. 4294967295 (dec) = FFFFFFFF (hex) is opaque white.
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(turn_off_color)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:SWITching:DISPlay:TOFF:COLor {param}')

	def get(self, power=repcap.Power.Default) -> int:
		"""POWer<*>:SWITching:DISPlay:TOFF:COLor \n
		Snippet: value: int = driver.power.switching.display.toff.color.get(power = repcap.Power.Default) \n
		The commands set the display color of the conduction area, non-conduction area, turn off area and turn on area,
		respectively. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: turn_off_color: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:DISPlay:TOFF:COLor?')
		return Conversions.str_to_int(response)
